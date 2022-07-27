import flask
from sqlalchemy import exc

from .. import utils
from . import login_required

def create_blueprint(auth, tokens, database, org_codes, *args, **kwargs):
    blueprint = flask.Blueprint(
        'org', __name__,
        template_folder='templates',
        url_prefix='/organization'
    )

    @blueprint.route("/<uuid:org_id>")
    def view(org_id):
        edit_mode = False
        admin = False

        current_user = auth.current_user() or flask.g.user
        if current_user:
            user_data = database.get_user_by_id(current_user['ID'])
            current_user['role'] = database.get_user_role(current_user['ID'])
            admin = current_user['role'] == 'admin'
            edit_mode = admin and user_data['OID'] == str(org_id)
        organization = database.get_organization_by_id(org_id)

        hierarchy = database.get_member_hierarchy(org_id)
        linear_hierarchy = []
        queue = [ (None, [], hierarchy) ]
        while len(queue) > 0:
            group, path, href = queue.pop(0)
            linear_hierarchy.append({
                'name': group,
                'path': path,
                'members': href['members']
            })
            for child, subhref in href['children'].items():
                ppath = [ *path ]
                if group: ppath.append(group)
                queue.append(( child, ppath, subhref ))

        return flask.render_template(
            "ui/organization.html.jinja",
            organization = organization,
            current_user = current_user,
            hierarchy = linear_hierarchy,
            groups = database.get_groups_by_organization(org_id),
            edit_mode=edit_mode,
            admin=admin
        )

    @blueprint.route("/create", methods=[ 'POST' ])
    @login_required(auth)
    def create():
        user     = auth.current_user() or flask.g.user
        org_code = org_codes.generate()

        params = {
            'OID'          : utils.new_uuid(),
            'Name'         : utils.get_field(flask.request, 'name'),
            'Code'         : org_code
        }

        database.execute((database.organization.insert(), params))
        database.remove_user_associations(user['ID'])
        database.update_user(user['ID'], { 'OID': params['OID'] })
        if database.get_user_role(user['ID']) != 'admin':
            database.execute((database.admin.insert(), { 'ID': user['ID'] }))

        return flask.redirect(flask.url_for("routes.users.current_user"))

    @blueprint.route("/join", methods=[ 'POST' ])
    @login_required(auth)
    def join():
        org_id = utils.get_field(flask.request, 'OID')
        code = utils.get_field(flask.request, 'code')
        result = database.get_organization_by_id(org_id)
        if not result or result.Code != code:
            flask.flash("Incorrect joining code. Specify the correct code to join.", category="danger")
        user = auth.current_user() or flask.g.user
        # Delete previous privileges
        if database.get_user_role(user['ID']) == 'admin':
            database.set_user_role(user['ID'], 'non-admin')
        database.remove_user_associations(user['ID'])
        database.update_user(user['ID'], { 'OID': result.OID })
        return flask.redirect(flask.url_for("routes.users.current_user")), 200

    @blueprint.route("/edit")
    @login_required(auth)
    def edit():
        current_user = auth.current_user() or flask.g.user
        user_data = database.get_user_by_id(current_user['ID'])
        params = {
            'Name'         : utils.get_field(flask.request, 'name'        , allow_null=True) or '',
            'Username'     : utils.get_field(flask.request, 'username'    , allow_null=True) or '',
            'Address'      : utils.get_field(flask.request, 'address'     , allow_null=True) or '',
            'Contact'      : utils.get_field(flask.request, 'contact'     , allow_null=True) or 0,
            'Email'        : utils.get_field(flask.request, 'e-mail'      , allow_null=True) or '',
            'Designation'  : utils.get_field(flask.request, 'designation' , allow_null=True) or '',
        }
        params = { param: params[param] for param in params if params[param] != user_data[param] }
        if params:
            try:
                if 'Username' in params and (not params['Username'] or database.get_user_by_ref(params['Username'])):
                    flask.flash("Username must be a non-empty and unique value.", category="danger")
                elif 'Email' in params and (not params['Email'] or database.get_user_by_ref(params['Email'])):
                    flask.flash("E-mail address must be a non-empty and unique value.", category="danger")
                else:
                    database.update_user(current_user['ID'], params)
                    flask.flash("User data updated successfully.", category="success")
            except exc.SQLAlchemyError as exception:
                print("SQL Exception:", exception)
                flask.flash("An unknown error has occurred. Try again later.", category="danger")
        return flask.redirect(flask.url_for("routes.users.current_user"))

    return blueprint