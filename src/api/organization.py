import flask

from .. import utils

def create_blueprint(auth, tokens, database, org_codes, *args, **kwargs):
    blueprint = flask.Blueprint(
        "org", __name__,
        template_folder="templates",
        url_prefix="/organization"
    )

    @blueprint.route("/join", methods=[ "POST" ])
    @auth.login_required
    def join():
        params = {
            'code': utils.get_field(flask.request, 'code'),
            'OID': utils.get_field(flask.request, 'OID')
        }
        result = database.get_organization_by_id(params['OID'])
        if not result or result.Code != params['code']:
            flask.abort(400, description="Specified organization does not exist")

        user = auth.current_user()
        database.remove_user_associations(user['ID'])
        database.update_user(user['ID'], { 'OID': result.OID })

        return flask.jsonify({
            'status': True,
            'code': 200,
            'data': { 'message': "User added successfully" }
        }), 200

    @blueprint.route("/create", methods=[ "POST" ])
    @auth.login_required
    def create():
        user     = auth.current_user()
        org_code = org_codes.generate()

        params = {
            'OID'          : utils.new_uuid(),
            'Name'         : utils.get_field(flask.request, 'name'),
            'Address'      : utils.get_field(flask.request, 'address'     , allow_null=True),
            'Website'      : utils.get_field(flask.request, 'website'     , allow_null=True),
            'Code'         : org_code
        }

        database.execute((database.organization.insert(), params))
        database.remove_user_associations(user['ID'])
        database.update_user(user['ID'], { 'OID': params['OID'] })
        if database.get_user_role(user['ID']) != 'admin':
            database.execute((database.admin.insert(), { 'ID': user['ID'] }))

        return flask.jsonify({
            'status': True,
            'code': 200,
            'data': params
        }), 200

    return blueprint
