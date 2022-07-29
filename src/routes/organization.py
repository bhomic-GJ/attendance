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
        database.remove_user_associations_and_migrate(user['ID'])
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
        database.remove_user_associations_and_migrate(user['ID'], result.OID)
        return flask.redirect(flask.url_for("routes.users.current_user")), 200

    @blueprint.route("/organization/renew_code", methods=[ 'POST' ])
    @login_required(auth, role='admin')
    def renew():
        user = auth.current_user() or flask.g.user
        user_data = database.get_user_by_id(user['ID'])
        org_code = org_codes.generate()
        database.execute((
            database.organization.update()\
                .where(database.organization.c.OID == user_data['OID'])\
                .values(Code=org_code), {}
        ))
        org_codes.reseed(database.get_organization_codes())
        return flask.redirect(flask.url_for("routes.org.view", org_id=user_data['OID']))

    @blueprint.route("/edit", methods=[ "POST" ])
    @login_required(auth)
    def edit():
        current_user = auth.current_user() or flask.g.user
        user_data = database.get_user_by_id(current_user['ID'])
        org_data  = database.get_organization_by_id(user_data['OID'])
        params = {
            'Name'   : utils.get_field(flask.request, 'name'   ),
            'Website': utils.get_field(flask.request, 'website', allow_null=True) or '',
            'Address': utils.get_field(flask.request, 'address', allow_null=True) or '',
        }
        params = { param: params[param] for param in params if params[param] != org_data[param] }
        if params:
            try:
                database.execute(
                    database.organization.update()\
                        .where(database.organization.c.OID == user_data['OID'])\
                        .values(**params)
                )
                flask.flash("Organization updated successfully.", category="success")
            except exc.SQLAlchemyError as exception:
                print("SQL Exception:", exception)
                flask.flash("An unknown error has occurred. Try again later.", category="danger")
        return flask.redirect(flask.url_for("routes.org.view", org_id=user_data['OID']))

    return blueprint