from . import db  # import the db object from __init__.py
from itsdangerous import URLSafeTimedSerializer as WebSerializer
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from . import login_manager
from flask import current_app, url_for
from .exceptions import ValidationError
import jwt
import hashlib
from datetime import datetime, timedelta
import bleach
import re

class Permission:
    FOLLOW = 1
    REVIEW = 2
    PUBLISH = 4
    MODERATE = 8
    ADMIN = 16
    
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm
    
    @staticmethod
    def insert_roles():
        roles = {
            'User':             [Permission.FOLLOW, Permission.REVIEW, Permission.PUBLISH],
            'Moderator':        [Permission.FOLLOW, Permission.REVIEW, Permission.PUBLISH, Permission.MODERATE],
            'Administrator':    [Permission.FOLLOW, Permission.REVIEW, Permission.PUBLISH, Permission.MODERATE, Permission.ADMIN],
        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer,
                            db.ForeignKey('users.id'),
                            primary_key=True)
    following_id = db.Column(db.Integer,
                             db.ForeignKey('users.id'),
                             primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(65), unique=True, nullable=False, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    # New column to store the hashed password
    password_hash = db.Column(db.String(128))

    # NEW column, true if user confirmed, false otherwise
    confirmed = db.Column(db.Boolean, default=False)
    
    # Extra profile info
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    bio = db.Column(db.Text())
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)

    avatar_hash = db.Column(db.String(32))

    compositions = db.relationship(
        'Composition',
        backref='artist',
        lazy='dynamic'
    )

    following = db.relationship(
        'Follow',
        foreign_keys=[Follow.follower_id],
        backref=db.backref('follower', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    followers = db.relationship(
        'Follow',
        foreign_keys=[Follow.following_id],
        backref=db.backref('following', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, following=user)
            db.session.add(f)

    def unfollow(self, user):
        f = self.following.filter_by(following_id=user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self, user):
        if user.id is None:
            return False
        return self.following.filter_by(
            following_id=user.id).first() is not None

    def is_a_follower(self, user):
        if user.id is None:
            return False
        return self.followers.filter_by(
            follower_id=user.id).first() is not None

    def email_hash(self):
        return hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()
    
    def unicornify(self, size=128):
        url = 'https://unicornify.pictures/avatar'
        hash_to_use = self.avatar_hash or self.email_hash()
        return f'{url}/{hash_to_use}?s={size}'

    def generate_confirmation_token(self, expiration_sec=3600):
        # For jwt.encode(), expiration is provided as a time in UTC
        # It is set through the "exp" key in the data to be tokenized
        expiration_time = datetime.utcnow() + timedelta(seconds=expiration_sec)
        data = {"exp": expiration_time, "confirm_id": self.id}
        # Use SHA-512 (known as HS512) for the hash algorithm
        token = jwt.encode(data, current_app.secret_key, algorithm="HS512")
        return token

    def confirm(self, token):
        try:
            data = jwt.decode(token, current_app.secret_key, algorithms=["HS512"])
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False

        if data.get("confirm_id") != self.id:
            return False

        self.confirmed = True
        db.session.add(self)
        return True
    
    @staticmethod
    def insert_default_role():
        user_role = Role.query.filter_by(name='User').first()
        if not user_role:
            user_role = Role(name='User')
            db.session.add(user_role)
            db.session.commit()
        return user_role
    
    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
        db.session.commit()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.role is None:
            self.role = self.insert_default_role()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = self.email_hash()
        if not self.is_following(self):
            self.follow(self)

    # Prevent direct reading of password
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    # When assigning password, store its hash instead of plain text
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    # Method to verify the password against the stored hash
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)
    
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    @property
    def followed_compositions(self):
        return Composition.query.join(
            Follow, Follow.following_id == Composition.artist_id
        ).filter(Follow.follower_id == self.id)
    
    def generate_auth_token(self, expiration_sec=3600):
        s = WebSerializer(current_app.config['SECRET_KEY'])
        return s.dumps({'id': self.id})
    
    @staticmethod
    def verify_auth_token(token):
        s = WebSerializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token, max_age=3600)
        except:
            return None
        return User.query.get(data['id'])
    
    def to_json(self):
        json_user = {
            'url': url_for('api.get_user', id=self.id),
            'username': self.username,
            'last_seen': self.last_seen.isoformat(),
            'compositions_url': url_for('api.get_user_compositions', id=self.id, _external=True),
            'followed_compositions_url': url_for('api.get_user_timeline', id=self.id, _external=True),
            'composition_count': self.compositions.count()
        }
        return json_user

def __repr__(self):
    return f"<User {self.username}>"

class ReleaseType:
    SINGLE = 1
    EXTENDED_PLAY = 2
    ALBUM = 3

class Composition(db.Model):
    __tablename__ = 'compositions'
    id = db.Column(db.Integer, primary_key=True)
    release_type = db.Column(db.Integer)
    title = db.Column(db.String(64))
    description = db.Column(db.Text)
    description_html = db.Column(db.Text)
    slug = db.Column(db.String(128), unique=True, index=True)
    timestamp = db.Column(
        db.DateTime,
        index=True,
        default=datetime.utcnow
    )
    artist_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    @property
    def release_type_label(self):
        mapping = {
            1: "Single",
            2: "EP",
            3: "Album"
        }
        return mapping.get(self.release_type, "Unknown")


    def __repr__(self):
        return f"<Composition {self.title}>"
    
    def generate_slug(self):
        self.slug = f"{self.id}-" + re.sub(r'[^\w]+', '-', self.title.lower())
        db.session.add(self)
        db.session.commit()
    
    @staticmethod
    def on_changed_description(target, value, oldvalue, initiator):
        allowed_tags = ['a']
        html = bleach.linkify(bleach.clean(value,
                                           tags=allowed_tags,
                                           strip=True))
        target.description_html = html

    def to_json(self):
        json_composition = {
            'url': url_for('api.get_composition', id=self.id, _external=True),
            'release_type': self.release_type_label,
            'title': self.title,
            'description': self.description,
            'description_html': self.description_html,
            'timestamp': self.timestamp.isoformat(),
            'artist_url': url_for('api.get_user', id=self.artist_id, _external=True)
        }
        return json_composition

    @staticmethod
    def from_json(json_composition):
        release_type = json_composition.get('release_type')
        title = json_composition.get('title')
        description = json_composition.get('description')
        
        if release_type is None:
            raise ValidationError("Composition must have a release type")
        if title is None:
            raise ValidationError("Composition must have a title")
        if description is None:
            raise ValidationError("Composition must have a description")
        
        return Composition(
            release_type=release_type,
            title=title,
            description=description
        )


db.event.listen(Composition.description,
                'set',
                Composition.on_changed_description)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class AnonymousUser(AnonymousUserMixin):
    def can(self, perm):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser

def __repr__(self):
    return f"<User {self.username}>"
