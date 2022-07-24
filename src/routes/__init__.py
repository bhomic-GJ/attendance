import json
import functools

import flask
from sqlalchemy import exc
from werkzeug import exceptions

def login_required(http_auth, role=None):
    if role and not isinstance(role, (list, tuple)):
        role = [ role ]
    def login_required_wrapper(callback):
        @functools.wraps(callback)
        def decorated_function(*args, **kwargs):
            user = http_auth.current_user() or flask.g.user
            if user is None:
                return flask.redirect(
                    flask.url_for('routes.auth.login')
                )
            flask.g.user = user
            user_roles = http_auth.get_user_roles(user)
            if not isinstance(user_roles, (list, tuple)):
                user_roles = [ user_roles ]
            if role:
                if not (set(role) & set(user_roles)):
                    flask.abort(401, "Unauthorized access based on assigned role")
            return callback(*args, **kwargs)
        return decorated_function
    return login_required_wrapper

from . import auth, users, organization, schedule

__version__ = "1.0"
__all__     = [ "users", "auth", "organization", "schedule" ]

def create_blueprint(*args, **kwargs):
    blueprint = flask.Blueprint(
        'routes', __name__,
        template_folder='templates',
    )

    # @blueprint.errorhandler(exceptions.HTTPException)
    # def handle_exception(e):
    #     return flask.render_template()
    #     response = e.get_response()
    #     response.data = json.dumps({
    #         'status': False,
    #         'code'  : e.code,
    #         'name'  : e.name,
    #         'error' : e.description
    #     })
    #     response.content_type = "application/json"

    #     return response

    # @blueprint.errorhandler(Exception)
    # def handle_generic_exception(e):
    #     return flask.render_template("ui/error.html.jinja", error=e), 500

    blueprint.register_blueprint(
        users.create_blueprint(*args, **kwargs)
    )
    blueprint.register_blueprint(
        organization.create_blueprint(*args, **kwargs)
    )
    blueprint.register_blueprint(
        schedule.create_blueprint(*args, **kwargs)
    )
    blueprint.register_blueprint(
        auth.create_blueprint(*args, **kwargs)
    )
    return blueprint
