import flask
from flask_sqlalchemy import SQLAlchemy

app = flask.Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@localhost:3306/attendance'

db = SQLAlchemy(app)

engine = db.create_engine(app.config['SQLALCHEMY_DATABASE_URI'], { 'echo': True })

@app.route("/")
def main():
    count = 100
    with engine.connect() as connection:
        result = connection.execute("SELECT COUNT(*) FROM USER")
        count = result.fetchone()[0]
    # return flask.render_template("dba_init_gj.html")
    return flask.render_template("index.jinja.html", count = count)