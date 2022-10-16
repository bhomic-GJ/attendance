import flask

from . import login_required

from .. import utils

def create_blueprint(auth, tokens, database, *args, **kwargs):
    blueprint = flask.Blueprint(
        'report', __name__,
        template_folder='templates',
        url_prefix='/report'
    )

    @blueprint.route("/")
    @login_required(auth)
    def home():
        user = auth.current_user() or flask.g.user
        user_data = database.get_user_by_id(user['ID'])

        group      = utils.get_field(flask.request, 'group', allow_null=True)
        start_date = utils.parse_date(utils.get_field(flask.request, 'start_date', allow_null=True) or '')
        end_date   = utils.parse_date(utils.get_field(flask.request, 'end_date', allow_null=True) or '')
        if start_date > end_date:
            flask.abort("Invalid date range for report generation.", category='warning')

        dates = []
        cdate = start_date
        while cdate <= end_date:
            dates.append(cdate)
            cdate = utils.modify_date(cdate, days=1)

        attendance = None
        if not group or start_date != end_date:
            attendance=[
                {
                    'schedule': { **schedule },
                    'attendance': [
                        database.get_attendance_record(
                            schedule.OID, schedule.GName, schedule.Start_Time,
                            schedule.Commencement_Date, date
                        ) for date in dates
                    ]
                }
                for schedule in database.get_schedules_for_group(user['ID'], group)
            ]
            for entry in attendance:
                transposed_data = [
                    [
                        entry['attendance'][j][i]
                        for j in range(len(entry['attendance']))
                    ]
                    for i in range(len(entry['attendance'][0]))
                ]
                entry['attendance'] = transposed_data

        return flask.render_template(
            "ui/report/home.html.jinja",
            current_user=user, dates=dates,
            attendance=attendance,
            groups=database.get_groups_by_organization(user_data['OID'])
        )

    return blueprint