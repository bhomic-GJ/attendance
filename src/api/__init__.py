import json

import flask
from sqlalchemy import exc
from werkzeug import exceptions

from . import users, organization, group

__version__ = "1.0"
__all__     = [ "users", "organization", "group" ]

def create_blueprint(*args, **kwargs):
    blueprint = flask.Blueprint(
        'api', __name__,
        template_folder='templates',
        url_prefix='/api'
    )

    @blueprint.errorhandler(exc.SQLAlchemyError)
    def handle_sql_exception(e):
        return flask.jsonify({
            'status': False,
            'code'  : 500,
            'name'  : "InternalServerError (SQLException)",
            'error' : str(e)
        }), 500

    @blueprint.errorhandler(exceptions.HTTPException)
    def handle_exception(e):
        response = e.get_response()
        response.data = json.dumps({
            'status': False,
            'code'  : e.code,
            'name'  : e.name,
            'error' : e.description
        })
        response.content_type = "application/json"
        return response

    blueprint.register_blueprint(
        users.create_blueprint(*args, **kwargs)
    )
    blueprint.register_blueprint(
        organization.create_blueprint(*args, **kwargs)
    )
    blueprint.register_blueprint(
        group.create_blueprint(*args, **kwargs)
    )
    # blueprint.register_blueprint(
    #     schedule.create_blueprint(*args, **kwargs)
    # )
    return blueprint
