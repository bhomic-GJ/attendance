import flask

from . import users

__version__ = "1.0"
__all__     = [ "users", "attendance" ]

def create_blueprint(database_engine):
    blueprint = flask.Blueprint(
        'api', __name__,
        template_folder='templates',
        url_prefix='api'
    )
    blueprint.register_blueprint(
        users.create_blueprint(database_engine)
    )
    return blueprint
