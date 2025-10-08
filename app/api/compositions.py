# app/api/compositions.py
from .. import db
from . import api
from flask import request, url_for, current_app, g, jsonify
from ..models import Composition, Permission
from .decorators import permission_required
from .errors import forbidden
from functools import wraps

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.current_user.can(permission):
                return forbidden("Insufficient permissions")
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@api.route('/compositions/')
def get_compositions():
    """Return all compositions paginated"""
    page = request.args.get('page', 1, type=int)
    pagination = Composition.query.paginate(
        page,
        per_page=current_app.config['RAGTIME_COMPS_PER_PAGE'],
        error_out=False
    )
    compositions = pagination.items
    prev = url_for('api.get_compositions', page=page-1) if pagination.has_prev else None
    next = url_for('api.get_compositions', page=page+1) if pagination.has_next else None
    return jsonify({
        'compositions': [c.to_json() for c in compositions],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })

@api.route('/compositions/<int:id>')
def get_composition(id):
    """Return a single composition"""
    composition = Composition.query.get_or_404(id)
    return jsonify(composition.to_json())

@api.route('/compositions/', methods=['POST'])
@permission_required(Permission.PUBLISH)
def new_composition():
    """Create a new composition"""
    composition = Composition.from_json(request.json)
    composition.artist = g.current_user
    db.session.add(composition)
    db.session.commit()

    composition.generate_slug()

    return jsonify(composition.to_json()), 201, {
        'Location': url_for('api.get_composition', id=composition.id)
    }

@api.route('/compositions/<int:id>', methods=['PUT'])
@permission_required(Permission.PUBLISH)
def edit_composition(id):
    """Edit a composition"""
    composition = Composition.query.get_or_404(id)

    if g.current_user != composition.artist and not g.current_user.can(Permission.ADMIN):
        return forbidden('Insufficient permissions')
    
    put_json = request.json
    composition.release_type = put_json.get('release_type', composition.release_type)
    composition.title = put_json.get('title', composition.title)
    composition.description = put_json.get('description', composition.description)
    
    db.session.add(composition)
    db.session.commit()
    return jsonify(composition.to_json())
