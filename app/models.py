from . import db  # import the db object from __init__.py
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from . import login_manager
from flask import current_app
import jwt
import hashlib
from datetime import datetime, timedelta

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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.role is None:
            self.role = self.insert_default_role()
        # Generar el hash de avatar si email existe y avatar_hash no
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = self.email_hash()

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
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.role is None:
            self.role = self.insert_default_role()

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
