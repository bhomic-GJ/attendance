import flask
from flask_sqlalchemy import SQLAlchemy

from src import api, utils

# import api

app = flask.Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost:3306/attendance'

db = SQLAlchemy(app)

engine = db.create_engine(app.config['SQLALCHEMY_DATABASE_URI'], { 'echo': True })

# app.register_blueprint(api.create_blueprint(engine))

@app.route("/")
def main():
    # count = 100
    # with engine.connect() as connection:
    #     result = connection.execute("SELECT COUNT(*) FROM USER")
    #     count = result.fetchone()[0]

    if flask.request.args.get('generate', None) is not None:
        qrpath = utils.qrcode.generate_qr("static/qr1.png", "https://github.com")
    else:
        qrpath = None

    return flask.render_template(
        "index.html.jinja",
        qrpath = qrpath
    )
