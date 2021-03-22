from flask import Blueprint, render_template

errors = Blueprint('errors', __name__)


@errors.app_errorhandler(404)  # decorator used to handle error 404
def error_404(error):
    return render_template('errors/404.html'), 404  # also return  the error code here


@errors.app_errorhandler(403)  # decorator used to handle error 403
def error_403(error):
    return render_template('errors/403.html'), 403  # also return  the error code here


@errors.app_errorhandler(500)  # decorator used to handle error 500
def error_500(error):
    return render_template('errors/500.html'), 500  # also return  the error code here
