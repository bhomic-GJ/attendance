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

    @blueprint.route("/register", methods=[ "GET", "POST" ])
    def register():
        in_get = flask.request.method == "GET"

        password  = utils.get_field(flask.request, 'password', allow_null=in_get)

        params = {
            'Name'         : utils.get_field(flask.request, 'name'    , allow_null=in_get),
            'Username'     : utils.get_field(flask.request, 'username', allow_null=in_get),
            'Email'        : utils.get_field(flask.request, 'e-mail'  , allow_null=True),
            'OID'          : None,
            'OJoin_Date'   : None
        }

        if flask.request.method == "POST":
            hashed_pw, salt = utils.hash_password(password)
            params.update({
                'ID'           : utils.new_uuid(),
                'Password_Hash': hashed_pw,
                'Password_Salt': salt,
            })

            try:
                database.execute((database.user.insert(), params))
                return flask.redirect(flask.url_for("routes.auth.login"))
            except Exception:
                flask.flash("An unexpected error occurred. Try again.", category='danger')

        return flask.render_template(
            "ui/register.html.jinja",
            **params
        )

    @blueprint.route("/logout")
    @login_required(auth)
    def logout():
        token = flask.session.pop('user_token')
        del tokens[token]
        return flask.redirect(flask.url_for("index"))
    return blueprint