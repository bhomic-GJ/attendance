import json

import flask
import flask_socketio

from . import login_required
from .. import utils

def create_blueprint(auth, tokens, database, socketio, *args, **kwargs):
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
        schedules = [
            database.get_schedules_for_user(user['ID'], date)
            for date in dates
        ]

        current_user = auth.current_user() or flask.g.user
        return flask.render_template(
            "ui/schedule_setter.html.jinja",
            current_user=current_user,
            dates=dates, schedules=schedules
        )

    @blueprint.route("/create", methods=[ 'POST' ])
    @login_required(auth, role='admin')
    def create():
        user = auth.current_user() or flask.g.user
        user_data = database.get_user_by_id(user['ID'])
        params = {
            'Creator'          : user['ID'],
            'GName'            : utils.get_field(flask.request, 'group'),
            'Start_Time'       : utils.parse_time(utils.get_field(flask.request, 'start_time')),
            'End_Time'         : utils.parse_time(utils.get_field(flask.request, 'end_time')),
            'Commencement_Date': utils.parse_date(utils.get_field(flask.request, 'start_date') or ''),
            'OID'              : user_data.OID,
            'Title'            : utils.get_field(flask.request, 'title', allow_null=True),
            'Status'           : utils.get_field(flask.request, 'status'),
            'Frequency'        : utils.get_field(flask.request, 'frequency')
        }

        database.execute((database.schedule.insert(), params))
        flask.flash(f"New schedule successfully registered for group {params['GName']}")
        return flask.redirect(flask.url_for("routes.sched.home"))

    @blueprint.route("/activate", methods=['POST'])
    @login_required(auth, role='admin')
    def activate():
        user = auth.current_user() or flask.g.user
        user_data = database.get_user_by_id(user['ID'])
        params = {
            'OID'              : user_data['OID'],
            'Start_Time'       : utils.get_field(flask.request, 'start_time'),
            'Commencement_Date': utils.get_field(flask.request, 'start_date'),
            'Creator'          : user['ID'],
            'GName'            : utils.get_field(flask.request, 'group'),
        }
        if not database.get_active_schedule(
            params['OID'], params['GName'], params['Creator'],
            params['Start_Time'], params['Commencement_Date']
        ):
            params['Token'] = utils.make_token(
                params['Commencement_Date'] + params['Start_Time'] + params['GName'], user_data['OID']
            )
            database.execute((database.active_schedule.insert(), params))
            flask.session['CurrentSchedule'] = params
        return flask.redirect(flask.url_for("routes.sched.view"))

    @blueprint.route("/view")
    @login_required(auth)
    def view():
        user = auth.current_user() or flask.g.user
        qr_url = None
        if database.get_user_role(user['ID']) == 'admin':
            params = flask.session.get('CurrentSchedule', None)
            if not params:
                return flask.redirect(flask.url_for("routes.sched.activate"))
            qr_url = flask.url_for(
                'static', filename=utils.qrcode.generate_qr(
                    json.dumps(params, indent=2, ensure_ascii=False),
                    "assets", "qr", prefix="static"
                )
            )
        return flask.render_template(
            "ui/attendance.html.jinja", current_user=user, qr_url=qr_url
        )

    @socketio.on('SYN')
    def init_handshake():
        flask_socketio.emit('SYN-ACK')

    @socketio.on('disconnect')
    def deactivate_schedule():
        user = auth.current_user() or flask.g.user
        if user:
            params = flask.session.get('CurrentSchedule', None)
            if params:
                database.delete_active_schedule(
                    params['OID'], params['GName'], params['Creator'],
                    params['Start_Time'], params['Commencement_Date']
                )
                del flask.session['CurrentSchedule']

    @blueprint.route("/attend", methods=['POST'])
    @login_required(auth)
    def mark_attendance():
        user = auth.current_user() or flask.g.user
        params = {
            'ID'               : user['ID'],
            'OID'              : utils.get_field(flask.request, 'OID'),
            'GName'            : utils.get_field(flask.request, 'group'),
            'Creator'          : utils.get_field(flask.request, 'creator'),
            'Start_Time'       : utils.get_field(flask.request, 'start_time'),
            'Commencement_Date': utils.get_field(flask.request, 'start_date')
        }
        token = utils.get_field(flask.request, 'token')
        schedule = database.get_active_schedule(
            params['OID'], params['GName'], params['Creator'],
            params['Start_Time'], params['Commencement_Date']
        )
        if not(schedule.Start_Time < utils.current_time() < schedule.End_Time):
            database.delete_active_schedule(
                params['OID'], params['GName'], params['Creator'],
                params['Start_Time'], params['Commencement_Date']
            )
            flask.flash("Specified schedule is no longer active.", category='danger')
        elif database.has_attendance_for_schedule(
            params['OID'], params['GName'], params['Creator'],
            params['Start_Time'], params['Commencement_Date']
        ):
            flask.flash("Attendance is already marked.", category='danger')
        elif token == schedule.Token:
            database.execute((database.attendance.insert(), params))
            flask.flash("Attendance marked successfully.", category='success')
            present_count = len(database.get_schedule_attendance(
                params['OID'], params['GName'], params['Creator'],
                params['Start_Time'], params['Commencement_Date']
            ))
            flask_socketio.emit('count_update', {
                'present': present_count,
                'absent': len(database.get_schedule_members(
                    params['OID'], params['GName'], params['Creator'],
                    params['Start_Time'], params['Commencement_Date']
                )) - present_count
            })
        else:
            flask.flash("Invalid operation on the current schedule. Try again.")
        return flask.redirect(flask.url_for("routes.sched.home"))

    return blueprint