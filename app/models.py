from . import db  # import the db object from __init__.py
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import login_manager
from flask import current_app
import jwt
from datetime import datetime, timedelta

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return f"<Role {self.name}>"

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

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def __repr__(self):
    return f"<User {self.username}>"
