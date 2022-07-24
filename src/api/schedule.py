import uuid
import string
import secrets
import datetime

import flask
import isodate
from sqlalchemy import sql, exc
from werkzeug import exceptions

from .. import utils

def create_blueprint(auth, tokens, database, *args, **kwargs):
    blueprint = flask.Blueprint(
        "schedule", __name__,
        template_folder="templates",
        url_prefix="/schedule"
    )

    @blueprint.route("/create", methods=[ "POST" ])
    @auth.login_required(role='admin')
    def create_schedule():
        start_date = isodate.parse_datetime(utils.get_field(flask.request, 'start_date'))

        if start_date < datetime.datetime.now():
            flask.abort(400, description="Invalid schedule commencement date")

        params = {
            'GName'            : utils.get_field(flask.request, 'group'),
            'OID'              : utils.get_field(flask.request, 'organization'),
            'Creator'          : auth.current_user()['ID'],
            'Start_Time'       : isodate.parse_time(utils.get_field(flask.request, 'start_time')),
            'End_Time'         : isodate.parse_time(utils.get_field(flask.request, 'end_time')),
            'Commencement_Date': start_date,
            'Status'           : utils.get_field(flask.request, 'status') or 0,
            'Frequency'        : utils.get_field(flask.request, 'frequency') or 1
        }

        database.execute(( database.schedule.insert(), params ))

        return flask.jsonify({
            'status': True,
            'code': 200,
            'data': params
        }), 200

    @blueprint.route("/activate", methods='POST')
    @auth.login_required(role='admin')
    def activate_schedule():
        pass

    @blueprint.route("/attend", methods='POST')
    @auth.login_required()
    def mark_attendance():
        pass

    @blueprint.route("/view", methods='POST')
    def get_schedules():
        pass

    return blueprint