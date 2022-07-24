import flask

from . import login_required

from .. import utils

def create_blueprint(auth, tokens, database, *args, **kwargs):
    blueprint = flask.Blueprint(
        'auth', __name__,
        template_folder='templates',
        url_prefix='/auth'
    )

    @blueprint.route("/login", methods=['GET', 'POST'])
    def login():
        if flask.request.method == "POST":
            username = utils.get_field(flask.request, 'username')
            password = utils.get_field(flask.request, 'password')

            result = database.get_user_by_ref(username)
            if result:
                if utils.verify_password(password, result.Password_Hash):
                    token, data = utils.make_token(result.Username, result.ID)
                    tokens[token] = data
                    flask.session['user_token'] = token
                    return flask.redirect(flask.url_for("index"))
            flask.flash("Failed to login. Invalid username/password.")
        return flask.render_template(
            "ui/login.html.jinja",
            username=utils.get_field(flask.request, 'username', allow_null=True) or '',
        )

    @blueprint.route("/register")
    def register():
        pass

    @blueprint.route("/logout")
    @login_required(auth)
    def logout():
        token = flask.session.pop('user_token')
        del tokens[token]
        return flask.redirect(flask.url_for("index"))
    return blueprint