import flask
import sqlalchemy

def create_blueprint(database):
    # USER_INSERT_QUERY = database.prepare(
    #     "INSERT INTO USER (ID, Name, Username, Password_Hash, Password_Salt, "
    #     "Address, Contact, email, Designation, OID, OJoinDate) "
    #     "VALUES (:ID, :Name, :Username, :Password_Hash, :Password_Salt, "
    #     ":Address, :Contact, :email, :Designation, :OID, :OJoinDate)"
    # )

    blueprint = flask.Blueprint(
        'users', __name__,
        template_folder='templates',
        url_prefix='users'
    )

    @blueprint.route('/create', method=[ 'POST' ])
    def create_user():
        # with database.connect() as connection:
        meta = sqlalchemy.MetaData(database)
        users = sqlalchemy.

    stm = select([cars])
    rs = con.execute(stm) 

    print rs.fetchall()
        pass

    return blueprint