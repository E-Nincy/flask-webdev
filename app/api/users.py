# app/api/users.py
from .. import db
from . import api
from flask import request, url_for, jsonify, g
from ..models import Permission, Composition, User
from .errors import forbidden
from .decorators import permission_required

@api.route('/users/<int:id>')
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.to_json())

@api.route('/users/<int:id>/compositions/')
def get_user_compositions(id):
    """Return all the compositions written by a user"""
    user = User.query.get_or_404(id)
    compositions = user.compositions.all()
    return jsonify({
        'compositions': [c.to_json() for c in compositions],
        'count': len(compositions)
    })

@api.route('/users/<int:id>/timeline/')
def get_user_timeline(id):
    """Return all the compositions followed by a user"""
    user = User.query.get_or_404(id)
    compositions = user.followed_compositions.all()
    return jsonify({
        'timeline': [c.to_json() for c in compositions],
        'count': len(compositions)
    })
