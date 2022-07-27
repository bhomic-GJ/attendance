import os
import time

import flask
import dotenv
from flask_httpauth   import HTTPTokenAuth
from flask_session    import Session
from flask_socketio   import SocketIO
from flask_sqlalchemy import SQLAlchemy

from src import api, routes, utils

# Load the environment variables specific to the app.
dotenv.load_dotenv()

app = flask.Flask(__name__)

app.config.update(
    SECRET_KEY                     = os.environ.get('SECRET_KEY', 'so_secret_much_wow'),
    SQLALCHEMY_TRACK_MODIFICATIONS = False,
    SQLALCHEMY_DATABASE_URI        = os.environ.get('DB_URL'),
    SESSION_TYPE                   = 'filesystem',
    SESSION_USE_SIGNER             = True
)

db       = SQLAlchemy(app)
socketio = SocketIO(app)
auth     = HTTPTokenAuth(scheme='Bearer')
# Initialize a filesystem based server-side session
Session(app)

tokens   = {}

engine   = db.create_engine(app.config['SQLALCHEMY_DATABASE_URI'], { 'echo': False })
database = utils.database.get_instance(engine)

# Initialize the code cache pool for generating new organization codes.
org_codes = utils.CodeGenerator(database.get_organization_codes())

@app.template_filter()
def field(date, fmtstr):
    return utils.format_date(date, fmtstr)

@app.before_request
def prepare_user():
    flask.g.user = None
    session_token = flask.session.get('user_token', None)
    if session_token and session_token in tokens:
        flask.g.user = tokens.get(session_token, None)
    elif session_token:
        flask.session.pop('user_token')

@auth.verify_token
def verify_token(token):
    for _token, data in tokens.items():
        if int(time.time()) - data['timestamp'] > 24 * 3600:
            del tokens[_token]
    if token in tokens:
        return tokens[token]

@auth.get_user_roles
def get_user_roles(user):
    if 'role' not in user:
        user['role'] = database.get_user_role(user['ID'])
    return user['role']

# Register the standard endpoints.
app.register_blueprint(
    routes.create_blueprint(
        auth, tokens, database,
        socketio=socketio,
        org_codes=org_codes
    )
)
# Register the API endpoint.
app.register_blueprint(
    api.create_blueprint(
        auth, tokens, database,
        socketio=socketio,
        org_codes=org_codes,
    )
)

@app.route("/playground", methods=["GET", "POST"])
def playground():
    return flask.jsonify({
        'method': flask.request.method,
        'headers': { **flask.request.headers },
        'args': { **flask.request.args },
        'form': { **flask.request.form },
        'session': { **flask.session },
        'tokens': { **tokens }
    })

@app.route("/attadm")
@routes.login_required(auth)
def attendance_admin():
    user = auth.current_user() or flask.g.user
    print(user['role'])
    qr_path = utils.qrcode.generate_qr("{ message: 'Hello world!' }", "assets", "static")
    return flask.render_template(
        "ui/attendance.html.jinja",
        current_user=user,
        qr_url=flask.url_for('static', filename=qr_path)
    )

@app.route("/")
def index():
    user = auth.current_user() or flask.g.user
    if user:
        return flask.redirect(flask.url_for("routes.users.current_user"))
    else:
        return flask.render_template(
            "ui/home_new_user.html.jinja",
            current_user=user
        )
