import flask
from flask_sqlalchemy import SQLAlchemy

app = flask.Flask(__name__)

@app.route("/")
def main():
    return flask.render_template("dba_init_gj.html")
    # return flask.render_template("index.jinja.html")