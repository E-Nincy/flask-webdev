import pytest
from app import create_app, db

@pytest.fixture(scope='module')
def new_app():
    # Setup: create app in testing mode
    app = create_app('testing')
    assert 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']  # opcional, para comprobar DB

    # create test client and context
    test_client = app.test_client()
    ctx = app.app_context()
    ctx.push()

    db.create_all()

    # test client
    yield test_client

    # Teardown
    db.session.remove()
    db.drop_all()
    ctx.pop()

