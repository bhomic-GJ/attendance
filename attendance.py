import os
import time

import flask
import dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPTokenAuth

from src import api, utils

# Load the environment variables specific to the app.
dotenv.load_dotenv()

app = flask.Flask(__name__)

app.config['SECRET_KEY']              = os.environ.get('SECRET_KEY', 'wow_so_secret')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URL')

db     = SQLAlchemy(app)
auth   = HTTPTokenAuth(scheme='Bearer')
tokens = {}

@auth.verify_token
def verify_token(token):
    for _token, data in tokens.items():
        if time.time() - data['timestamp'] > 24 * 3600:
            del tokens[_token]
    print(tokens)
    if token in tokens:
        return tokens[token]

engine   = db.create_engine(app.config['SQLALCHEMY_DATABASE_URI'], { 'echo': True })
database = utils.database.get_instance(engine)

app.register_blueprint(
    api.create_blueprint(auth, tokens, database)
)

@app.route("/QR")
def qr():
    return flask.render_template("Qr2.html")

@app.route("/login")
def login():
    return flask.render_template("ui/login.html.jinja")

@app.route("/")
def main():
    # if flask.request.args.get('generate', None) is not None:
    #     qrpath = utils.qrcode.generate_qr("static/qr1.png", "https://github.com")
    # else:
    #     qrpath = None

    return flask.render_template(
        "ui/home_existing_user.html.jinja"
    )
