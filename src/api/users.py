import flask

from .. import utils

def create_blueprint(auth, tokens, database, *args, **kwargs):
    """ Creates a blueprint for exposing routes related the users section of the API

    Args:
        auth (flask_httpauth.HTTPTokenAuth): The flask http authentication object for restricting access
        tokens (dict): The currently maintained set of tokens for logged in users.
        database (sqlalchemy.engine.Engine): The engine object associated with the currently connected database.
        org_codes (utils.CodeGenerator): Generator for organization codes.

    Returns:
        flask.Blueprint: The blueprint object to register in the flask application.
    """

    blueprint = flask.Blueprint(
        'users', __name__,
        template_folder='templates',
        url_prefix='/users'
    )

    @blueprint.route('/view')
    @auth.login_required
    def view_user():
        user = auth.current_user()
        result = database.get_user_by_id(user['ID'])
        del result['Password_Hash']
        del result['Password_Salt']
        result['role'] = database.get_user_role(result['ID'])
        return flask.jsonify(result)

    @blueprint.route('/login', methods=[ 'POST' ])
    def login_user():
        username = utils.get_field(flask.request, 'username')
        password = utils.get_field(flask.request, 'password')

        result = database.get_user_by_ref(username)
        if not result:
            flask.abort(401, description="Failed to login user")
        if not utils.verify_password(password, result.Password_Hash):
            flask.abort(401, description="Failed to login user")

        token, data = utils.make_token(result.Username, result.ID)
        tokens[token] = data

        return flask.jsonify({
            'status': True,
            'code': 200,
            'username': result.Username,
            'token': token
        }), 200

    @blueprint.route('/create', methods=[ 'POST' ])
    def create_user():
        password  = utils.get_field(flask.request, 'password')
        hashed_pw, salt = utils.hash_password(password)
        organization = utils.get_field(flask.request, 'organization', allow_null=True)

        params = {
            'ID'           : utils.new_uuid(),
            'Name'         : utils.get_field(flask.request, 'name'),
            'Username'     : utils.get_field(flask.request, 'username'),
            'Password_Hash': hashed_pw,
            'Password_Salt': salt,
            'Address'      : utils.get_field(flask.request, 'address'     , allow_null=True),
            'Contact'      : utils.get_field(flask.request, 'contact'     , allow_null=True) or 0,
            'Email'        : utils.get_field(flask.request, 'e-mail'      , allow_null=True),
            'Designation'  : utils.get_field(flask.request, 'designation' , allow_null=True),
            'OID'          : organization,
        }
        if not organization: params['OJoin_Date'] = None

        database.execute((database.user.insert(), params))

        result = database.get_user_by_id(params['ID'])
        del result['Password_Hash']
        del result['Password_Salt']
        return flask.jsonify({
            'status': True,
            'code': 200,
            'data': result
        }), 200

    return blueprint