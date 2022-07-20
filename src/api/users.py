import uuid
import json
import time
import base64

import flask
import bcrypt
from sqlalchemy import sql, exc
from werkzeug import exceptions

from .. import utils

def create_blueprint(auth, tokens, database):
    """ Creates a blueprint for exposing routes related the users section of the API

    Args:
        auth (flask_httpauth.HTTPTokenAuth): The flask http authentication object for restricting access
        tokens (dict): The currently maintained set of tokens for logged in users.
        database (sqlalchemy.engine.Engine): The engine object associated with the currently connected database.

    Returns:
        flask.Blueprint: The blueprint object to register in the flask application.
    """

    blueprint = flask.Blueprint(
        'users', __name__,
        template_folder='templates',
        url_prefix='/users'
    )

    @auth.get_user_roles
    def get_user_roles(user):
        if 'role' not in user:
            result = database.execute((
                sql.select([ database.admin ]).where(
                    database.admin.c.ID == sql.bindparam('ID')
                ),
                { 'ID': user['ID'] }
            ))[0]
            user['role'] = 'admin' if result.count() else 'non-admin'
        return user['role']

    @blueprint.route('/view')
    @auth.login_required
    def view_user():
        user = auth.current_user()
        return flask.jsonify(user)

    @blueprint.route('/login', methods=[ 'POST' ])
    def login_user():
        username = utils.get_field(flask.request, 'username')
        password = utils.get_field(flask.request, 'password')
        
        query = sql.select([
            database.user.c.ID,
            database.user.c.Username,
            database.user.c.Password_Hash,
            database.user.c.Password_Salt
        ]).where(sql.or_(
            database.user.c.Username == sql.bindparam('param'),
            database.user.c.Email == sql.bindparam('param')
        ))

        print(query)
        result = database.execute((query, { 'param': username }))[0]
        result = result.fetchone()

        if not result:
            raise exceptions.Unauthorized("Failed to login user?")
        password_hash = base64.b64decode(result['Password_Hash'])
        if not bcrypt.checkpw(password.encode(), password_hash):
            raise exceptions.Unauthorized("Failed to login user")

        ids = uuid.uuid4(), uuid.uuid1()
        token = base64.urlsafe_b64encode(
            result['Username'].encode() + b':'
            + ids[0].bytes + b':' + ids[1].bytes
        ).decode('ascii')
    
        tokens[token] = {
            'username': result['Username'],
            'ID': result['ID'],
            'timestamp': time.time()
        }

        return flask.jsonify({
            'status': True,
            'code': 200,
            'username': result['Username'],
            'token': token
        }), 200

    @blueprint.route('/create', methods=[ 'POST' ])
    def create_user():
        password  = utils.get_field(flask.request, 'password')
        salt      = bcrypt.gensalt()
        hashed_pw = bcrypt.hashpw(password.encode(), salt)
        
        params = {
            'ID'           : str(uuid.uuid4()),
            'Name'         : utils.get_field(flask.request, 'name'),
            'Username'     : utils.get_field(flask.request, 'username'),
            'Password_Hash': base64.b64encode(hashed_pw).decode('ascii'),
            'Password_Salt': base64.b64encode(salt).decode('ascii'),
            'Address'      : utils.get_field(flask.request, 'address'     , allow_null=True),
            'Contact'      : utils.get_field(flask.request, 'contact'     , allow_null=True) or 0,
            'Email'        : utils.get_field(flask.request, 'e-mail'      , allow_null=True),
            'Designation'  : utils.get_field(flask.request, 'designation' , allow_null=True),
            'OID'          : utils.get_field(flask.request, 'organization'),
            'OJoin_Date'   : None
        }

        database.execute((database.user.insert(), params))

        del params['Password_Hash']
        del params['Password_Salt']
        return flask.jsonify({
            'status': True,
            'code': 200,
            'data': params
        }), 200

    return blueprint