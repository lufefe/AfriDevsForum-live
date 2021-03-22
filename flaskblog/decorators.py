from functools import wraps

from flask import abort
from flask_login import current_user

from flaskblog.models import Permission


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def admin_required(f):
    return permission_required(Permission.ADMINISTRATOR)(f)


def moderator_required(f):
    return permission_required(Permission.MODERATE_COMMENTS)(f)


def user_required(f):
    return permission_required(Permission.WRITE_ARTICLES)
