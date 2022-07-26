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

        user = auth.current_user() or flask.g.user
        schedules = database.get_schedules_for_user(user['ID'])

        current_user = auth.current_user() or flask.g.user
        return flask.render_template(
            "ui/schedule_setter.html.jinja",
            current_user=current_user,
            dates=dates
        )

    @blueprint.route("/create", methods=[ 'POST' ])
    @login_required(auth, role='admin')
    def create():
        user = auth.current_user() or flask.g.user
        user_data = database.get_user_by_id(user['ID'])
        params = {
            'Creator': user['ID'],
            'GName': utils.get_field(flask.request, 'group'),
            'Start_Time': utils.parse_time(utils.get_field(flask.request, 'start_time')),
            'End_Time': utils.parse_time(utils.get_field(flask.request, 'end_time')),
            'Commencement_Date': utils.parse_date(utils.get_field(flask.request, 'start_date') or ''),
            'OID': user_data.OID,
            'Title': utils.get_field(flask.request, 'title', allow_null=True),
            'Status': utils.get_field(flask.request, 'status'),
            'Frequency': utils.get_field(flask.request, 'frequency')
        }

        database.execute((database.schedule.insert(), params))
        flask.flash(f"New schedule successfully registered for group {params['GName']}")
        return flask.redirect(flask.url_for("routes.sched.home"))

    return blueprint