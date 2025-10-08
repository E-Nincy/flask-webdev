# app/api/__init__.py
from flask import Blueprint

# Create Blueprint
api = Blueprint('api', __name__, url_prefix='/api/v1')

@api.route('/')
def index():
    return {}

from . import authentication, comments, compositions, errors, users
