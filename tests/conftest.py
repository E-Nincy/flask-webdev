import pytest
from app import create_app, db
from app.models import Role, User
from flask_login import LoginManager

@pytest.fixture(scope="module")
def app():
    # Create the app in testing mode
    app = create_app("testing")
    ctx = app.app_context()
    ctx.push()
     
    from app import login_manager
    login_manager.login_view = None

    db.create_all()
    Role.insert_roles()
    yield app
    db.session.remove()
    db.drop_all()
    ctx.pop()

@pytest.fixture
def client(app):
    # Provide a test client
    return app.test_client()

@pytest.fixture
def user(app):
    # Create a user with a unique email for each test
    role = Role.query.filter_by(name="User").first()
    u = User(username="testuser", email="unique@test.com", password="password", role=role)
    db.session.add(u)
    db.session.commit()
    return u


