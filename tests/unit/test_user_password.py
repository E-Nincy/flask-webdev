# tests/unit/test_user_password.py
import pytest
from app.models import User
from app import db

def test_create_user_with_password(new_app):
    # Test that a new user with a password can be created
    u = User(username='alice', email='alice@example.com')
    u.password = 'mypassword'
    db.session.add(u)
    db.session.commit()

    assert u.password_hash is not None  # Password hash should be generated
    assert u.username == 'alice'
    assert u.email == 'alice@example.com'

def test_verify_password(new_app):
    # Test that a user's password can be verified successfully or fail
    u = User(username='bob', email='bob@example.com')
    u.password = 'secret123'
    db.session.add(u)
    db.session.commit()

    assert u.verify_password('secret123') is True  # Correct password
    assert u.verify_password('wrongpassword') is False  # Incorrect password

def test_password_field_raises_exception(new_app):
    # Test that accessing the user's password field raises an AttributeError
    u = User(username='carol', email='carol@example.com')
    u.password = 'foobar'
    db.session.add(u)
    db.session.commit()

    with pytest.raises(AttributeError):
        _ = u.password

def test_same_password_different_hashes(new_app):
    # Test that two users with the same password have different password hashes
    u1 = User(username='dave', email='dave@example.com')
    u2 = User(username='eve', email='eve@example.com')

    u1.password = 'samepassword'
    u2.password = 'samepassword'

    db.session.add(u1)
    db.session.add(u2)
    db.session.commit()

    assert u1.password_hash != u2.password_hash