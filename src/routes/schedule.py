import json

import flask
import flask_socketio

from . import login_required
from .. import utils

def create_blueprint(auth, tokens, database, socketio, admins, *args, **kwargs):
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
        # Snap date to nearest monday, for use in FullCalendar
        if (weekday := start_date.weekday()) != 0:
            start_date = utils.modify_date(start_date, days=-weekday)
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
            dates=dates, schedules=schedules,
            user_groups=database.get_user_groups(current_user['ID'])
        )

    @blueprint.route("/create", methods=[ 'POST' ])
    @login_required(auth, role='admin')
    def create():
        user = auth.current_user() or flask.g.user
        user_data = database.get_user_by_id(user['ID'])
        params = {
            'Creator'          : user['ID'],
            'GName'            : utils.get_field(flask.request, 'group'),
            'Start_Time'       : utils.format_date(utils.parse_time(utils.get_field(flask.request, 'start_time')), "%H:%M:%S"),
            'End_Time'         : utils.format_date(utils.parse_time(utils.get_field(flask.request, 'end_time')), "%H:%M:%S"),
            'Commencement_Date': utils.parse_date(utils.get_field(flask.request, 'start_date') or ''),
            'OID'              : user_data.OID,
            'Title'            : utils.get_field(flask.request, 'title', allow_null=True),
            'Status'           : utils.get_field(flask.request, 'status'),
            'Frequency'        : utils.get_field(flask.request, 'frequency')
        }

        database.execute((database.schedule.insert(), params))
        flask.flash(f"New schedule successfully registered for group {params['GName']}.", category='success')
        return flask.redirect(flask.url_for("routes.sched.home"))

    @blueprint.route("/activate", methods=['POST'])
    @login_required(auth, role='admin')
    def activate():
        user = auth.current_user() or flask.g.user
        user_data = database.get_user_by_id(user['ID'])
        params = {
            'OID'              : user_data['OID'],
            'Start_Time'       : utils.parse_time(utils.get_field(flask.request, 'start_time')).replace(tzinfo=None),
            'Commencement_Date': utils.parse_date(utils.get_field(flask.request, 'start_date')),
            'Creator'          : user['ID'],
            'GName'            : utils.get_field(flask.request, 'group'),
        }
        if not database.get_active_schedule(
            params['OID'], params['GName'],
            params['Start_Time'], params['Commencement_Date']
        ):
            if not database.can_activate_schedule(
                params['OID'], params['GName'], params['Creator'],
                params['Start_Time'], params['Commencement_Date'],
                utils.parse_date('')
            ):
                flask.flash("Cannot activate schedule: Invalid access / unmet time range constraints.", category='danger')
                return flask.redirect(flask.url_for("routes.sched.home"))
            else:
                params['Token'] = utils.make_token(
                    str(params['Commencement_Date']) + str(params['Start_Time']) + params['GName'], user_data.OID
                )[0]
                database.execute((database.active_schedule.insert(), params))
                flask.session['CurrentSchedule'] = params
        return flask.redirect(flask.url_for("routes.sched.view"), code=307)

    @blueprint.route("/view", methods=["POST"])
    @login_required(auth)
    def view():
        user = auth.current_user() or flask.g.user
        qr_url = None
        if database.get_user_role(user['ID']) == 'admin':
            user_data = database.get_user_by_id(user['ID'])
            params = {
                'OID'              : user_data['OID'],
                'Start_Time'       : utils.parse_time(utils.get_field(flask.request, 'start_time')).replace(tzinfo=None),
                'Commencement_Date': utils.parse_date(utils.get_field(flask.request, 'start_date')),
                'Creator'          : user['ID'],
                'GName'            : utils.get_field(flask.request, 'group'),
            }
            session_params = flask.session.get('CurrentSchedule', None)
            if session_params: params.update(Token=session_params['Token'])
            if not session_params or session_params != params:
                return flask.redirect(flask.url_for("routes.sched.activate"), code=307)
            params['Start_Time']        = str(params['Start_Time'])
            params['Commencement_Date'] = str(params['Commencement_Date'])
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
    def init_handshake(_):
        user = flask.session.get('user_token', None)
        if user: user = tokens[user]
        if user: admins[user['ID']] = flask.request.sid
        params = flask.session.get('CurrentSchedule', None)
        if params:
            present_count = len(database.get_schedule_attendance(
                params['OID'], params['GName'],
                params['Start_Time'], params['Commencement_Date'],
                utils.parse_date('').replace(tzinfo=None)
            ))
            flask_socketio.emit('SYN-ACK', {
                'present': present_count,
                'absent': len(database.get_schedule_members(
                    params['OID'], params['GName']
                )) - present_count
            }, to=admins[user['ID']])
            return
        flask_socketio.emit('SYN-ACK', { 'present': 0, 'absent': 0 })

    @socketio.on('disconnect')
    def deactivate_schedule():
        params = flask.session.get('CurrentSchedule', None)
        if params:
            database.delete_active_schedule(
                params['OID'], params['GName'], params['Creator'],
                params['Start_Time'], params['Commencement_Date']
            )
            del flask.session['CurrentSchedule']
            if params['Creator'] in admins:
                del admins[params['Creator']]

    @blueprint.route("/attend", methods=['POST'])
    @login_required(auth)
    def mark_attendance():
        user = auth.current_user() or flask.g.user
        user_data = database.get_user_by_id(user['ID'])
        params = {
            'ID'               : user['ID'],
            'OID'              : utils.get_field(flask.request, 'OID'),
            'GName'            : utils.get_field(flask.request, 'GName'),
            'Creator'          : utils.get_field(flask.request, 'Creator'),
            'Start_Time'       : utils.parse_time(utils.get_field(flask.request, 'Start_Time')),
            'Commencement_Date': utils.parse_date(utils.get_field(flask.request, 'Commencement_Date'))
        }
        if user_data['OID'] != params['OID'] or params['GName'] not in database.get_user_groups(user['ID']):
            flask.flash("Cannot mark attendance in non-member group schedules", category='danger')
            return flask.redirect(flask.url_for("routes.sched.home"))
        token = utils.get_field(flask.request, 'Token')
        schedule = database.get_active_schedule(
            params['OID'], params['GName'],
            params['Start_Time'], params['Commencement_Date']
        )
        if not(schedule.Start_Time < utils.current_time().replace(tzinfo=None) < schedule.End_Time):
            database.delete_active_schedule(
                params['OID'], params['GName'], params['Creator'],
                params['Start_Time'], params['Commencement_Date']
            )
            flask.flash("Specified schedule is no longer active.", category='danger')
        elif database.has_attendance_for_schedule(
            params['ID'], utils.parse_date(''), params['OID'], params['GName'],
            params['Start_Time'], params['Commencement_Date']
        ):
            flask.flash("Attendance is already marked.", category='info')
        elif token == schedule.Token:
            params['Commencement_Date'] = params['Commencement_Date'].replace(tzinfo=None)
            params['Start_Time'] = params['Start_Time'].replace(tzinfo=None)
            database.execute((database.attendance.insert(), params))
            flask.flash("Attendance marked successfully.", category='success')
            present_count = len(database.get_schedule_attendance(
                params['OID'], params['GName'],
                params['Start_Time'], params['Commencement_Date'],
                utils.parse_date('').replace(tzinfo=None)
            ))
            if params['Creator'] in admins:
                socketio.emit('count_update', {
                    'present': present_count,
                    'absent': len(database.get_schedule_members(
                        params['OID'], params['GName']
                    )) - present_count
                }, room=admins[params['Creator']], to=admins[params['Creator']])
        else:
            flask.flash("Invalid operation on the current schedule. Try again.", category='danger')
        return flask.redirect(flask.url_for("routes.sched.home"))

    return blueprint