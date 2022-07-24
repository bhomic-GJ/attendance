import flask

from . import login_required
from .. import utils

def create_blueprint(auth, tokens, database, *args, **kwargs):
    """ Creates a blueprint for exposing routes related the users section of the API

    Args:
        auth (flask_httpauth.HTTPTokenAuth): The flask http authentication object for restricting access
        tokens (dict): The currently maintained set of tokens for logged in users.
        database (sqlalchemy.engine.Engine): The engine object associated with the currently connected database.

    Returns:
        flask.Blueprint: The blueprint object to register in the flask application.
    """

    blueprint = flask.Blueprint(
        'sched', __name__,
        template_folder='templates',
        url_prefix='/schedule'
    )

    @blueprint.route('/')
    @login_required(auth)
    def home():
        start_date = utils.get_field(flask.request, 'start_date', allow_null=True)
        start_date = utils.parse_date(start_date or '')
        dates = [ utils.modify_date(start_date, days=i) for i in range(7) ]

        current_user = auth.current_user() or flask.g.user
        return flask.render_template(
            "ui/schedule_setter.html.jinja",
            current_user=current_user,
            dates=dates
        )

    return blueprint