import flask

from . import login_required
from .. import utils

def create_blueprint(auth, tokens, database, *args, **kwargs):
    blueprint = flask.Blueprint(
        "group", __name__,
        template_folder="templates",
        url_prefix="/group"
    )

    @blueprint.route("/move", methods=[ "POST" ])
    @login_required(auth, role='admin')
    def move():
        user = auth.current_user() or flask.g.user
        user_data = database.get_user_by_id(user['ID'])

        user_ids      = utils.get_field(flask.request, 'user_ids')
        if isinstance(user_ids, str): user_ids = [ user_ids ]
        user_ids      = set(user_ids)
        group         = utils.get_field(flask.request, 'group', allow_null=True) or None
        current_group = utils.get_field(flask.request, 'current_group', allow_null=True) or None

        old_members = {
            member
            for cgrp in database.get_parent_chain(user_data['OID'], current_group)
                for member in database.get_members(user_data['OID'], cgrp)
        }
        old_ids = { member.ID for member in old_members }
        old_admins = { member.ID for member in old_members if member.Role == 'admin' }
        left_admin_count = len(old_admins - user_ids)
        left_user_count  = len(old_ids    - user_ids)
        if left_admin_count == 0 and left_user_count != 0:
            flask.flash("Cannot migrate all admin users from the group chain, would render group useless.", category='danger')
        else:
            queries = []
            if current_group is not None:
                queries.append((
                    database.membership.delete()\
                        .where(database.membership.c.ID.in_(user_ids))\
                        .where(database.membership.c.GName == current_group)\
                        .where(database.membership.c.OID == user_data['OID']), {}
                ))
            if group is not None:
                queries.append((
                    database.membership.insert(), [
                        { 'ID': user_id, 'GName': group, 'OID': user_data['OID'] }
                        for user_id in user_ids
                    ]
                ))
            database.execute(queries)
        return flask.redirect(flask.url_for("routes.org.view", org_id=user_data['OID']))

    @blueprint.route("/create", methods=[ "GET", "POST" ])
    @login_required(auth, role = 'admin')
    def create():
        user = auth.current_user() or flask.g.user
        user_data = database.get_user_by_id(user['ID'])

        in_get = flask.request.method == "GET"

        params = {
            'Name'   : utils.get_field(flask.request, 'name', allow_null=in_get),
            'OID'    : user_data['OID'],
            'Creator': user['ID'],
        }
        parent = utils.get_field(flask.request, 'parent', allow_null=True)

        if flask.request.method == "POST":
            queries = [ ( database.group.insert(), params ) ]
            if parent:
                gh_params = {
                    'Name'  : params['Name'],
                    'Parent': parent,
                    'OID'   : params['OID']
                }
                queries.append(( database.group_hierarchy.insert(), gh_params ))

            database.execute(*queries)

            return flask.redirect(flask.url_for("routes.org.view", org_id=user_data['OID']))
        else:
            return flask.render_template(
                "ui/group_page.html.jinja",
                **params, current_user=user,
                groups=database.get_groups_by_organization(params['OID'])
            )

    return blueprint
