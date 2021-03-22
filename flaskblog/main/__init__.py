from flaskblog.main.routes import main
from flaskblog.models import Permission


@main.app_context_processor
def inject_permissions():
    return dict(Permission = Permission)
