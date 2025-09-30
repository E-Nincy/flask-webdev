import pytest
from app import db
from app.models import Role, User, Permission

@pytest.fixture
def setup_roles(app):
    """Setup roles before each test."""
    with app.app_context():
        Role.insert_roles()
        yield
        db.session.rollback()

def create_user(username, email, password="password", role=None):
    """Helper to create a user with password and optional role."""
    u = User(username=username, email=email)
    u.password = password  # automatically hashes the password
    if role:
        u.role = role
    db.session.add(u)
    db.session.commit()
    return u

def test_insert_roles_creates_roles(app, setup_roles):
    """Test that roles are created correctly with proper permissions."""
    with app.app_context():
        user_role = Role.query.filter_by(name="User").first()
        mod_role = Role.query.filter_by(name="Moderator").first()
        admin_role = Role.query.filter_by(name="Administrator").first()

        assert user_role is not None
        assert mod_role is not None
        assert admin_role is not None

        # Check permissions
        assert user_role.has_permission(Permission.FOLLOW)
        assert not user_role.has_permission(Permission.ADMIN)

        assert mod_role.has_permission(Permission.MODERATE)
        assert not mod_role.has_permission(Permission.ADMIN)

        assert admin_role.has_permission(Permission.ADMIN)

def test_user_has_default_role(app, setup_roles):
    """Test that a new user gets the 'User' role by default."""
    with app.app_context():
        u = create_user("simon", "test@example.com")
        assert u.role is not None
        assert u.role.name == "User"
        assert u.can(Permission.FOLLOW)
        assert not u.can(Permission.ADMIN)

def test_permission_helpers(app, setup_roles):
    """Test the helper methods can() and is_administrator()."""
    with app.app_context():
        admin_role = Role.query.filter_by(name="Administrator").first()
        u = create_user("admin", "admin@example.com", role=admin_role)
        assert u.can(Permission.ADMIN)
        assert u.is_administrator()

def test_admin_required_view(client, app, setup_roles):
    """Test that the /admin route is only accessible by admins."""
    with app.app_context():
        # Create normal user
        create_user("user", "user@example.com", "password")
        admin_role = Role.query.filter_by(name="Administrator").first()
        create_user("admin", "admin@example.com", "password", role=admin_role)

        with client:
            # Login as normal user
            client.post("/login", data={"email": "user@example.com", "password": "password"}, follow_redirects=True)
            response = client.get("/admin")
            # Normal users should be forbidden
            assert response.status_code == 403

            # Logout and login as admin
            client.get("/logout", follow_redirects=True)
            client.post("/login", data={"email": "admin@example.com", "password": "password"}, follow_redirects=True)
            response = client.get("/admin")
            # Admin should access successfully
            assert response.status_code == 200
            assert b"Welcome, administrator!" in response.data

def test_permission_required_view(client, app, setup_roles):
    """Test that the /moderate route is only accessible by moderators."""
    with app.app_context():
        # Create normal user
        create_user("user2", "user2@example.com", "password")
        mod_role = Role.query.filter_by(name="Moderator").first()
        create_user("mod", "mod@example.com", "password", role=mod_role)

        with client:
            # Login as normal user
            client.post("/login", data={"email": "user2@example.com", "password": "password"}, follow_redirects=True)
            response = client.get("/moderate")
            # Normal users should be forbidden
            assert response.status_code == 403

            # Logout and login as moderator
            client.get("/logout", follow_redirects=True)
            client.post("/login", data={"email": "mod@example.com", "password": "password"}, follow_redirects=True)
            response = client.get("/moderate")
            # Moderator should access successfully
            assert response.status_code == 200
            assert b"Greetings, moderator!" in response.data
