from flask import render_template
from . import main

@main.app_errorhandler(403)
def forbidden(e):
    return render_template('error.html', error_title="Forbidden",
                           error_msg="You shouldn't be here!"), 403

@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_title="Not Found",
                           error_msg="That page doesn't exist"), 404

@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template("error.html", error_title="Internal Server Error",
                           error_msg="Sorry, we seem to be experiencing technical difficulties"), 500

