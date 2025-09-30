import pytest
from app import create_app, db
from app.models import User
from datetime import datetime, timedelta

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def user(app): 
    u = User(username='testuser', email='test@test.com', password='password')
    db.session.add(u)
    db.session.commit()
    return u

def test_confirmation_token_valid(user):
    token = user.generate_confirmation_token()
    assert user.confirm(token) is True
    assert user.confirmed is True

def test_confirmation_token_expired(user, monkeypatch):
    token = user.generate_confirmation_token(expiration_sec=1)
    # Simular que pasa tiempo para que caduque
    import time
    time.sleep(2)
    assert user.confirm(token) is False

def test_confirmation_token_invalid(user):
    fake_token = "invalid.token.here"
    assert user.confirm(fake_token) is False
