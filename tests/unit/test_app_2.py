# tests/unit/test_app_2.py
from app import db
from app.models import User

def test_database_insert(new_app): 
    u = User(email='john@example.com', username='john')
    db.session.add(u)
    db.session.commit()

    # Comprobamos que se guardó
    assert User.query.count() == 1
    user = User.query.first()
    assert user.username == 'john'

