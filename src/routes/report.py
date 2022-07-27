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
        return flask.render_template(
            "ui/report/home.html.jinja",
            current_user=user
        )

    return blueprint