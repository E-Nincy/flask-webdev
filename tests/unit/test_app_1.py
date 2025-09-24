from flask import current_app

def test_current_app(new_app):
    assert current_app
    assert current_app.config['TESTING'] is True
