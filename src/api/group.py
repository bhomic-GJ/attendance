import uuid
import string
import secrets

import flask
from sqlalchemy import sql, exc
from werkzeug import exceptions

from .. import utils

def create_blueprint(auth, tokens, database, *args, **kwargs):
    blueprint = flask.Blueprint(
        "group", __name__,
        template_folder="templates",
        url_prefix="/group"
    )

    def flatten_member_hierarchy(hierarchy):
        members = []
        queue = [ hierarchy ]
        while len(queue) > 0:
            href = queue.pop(0)
            for child in href['children']:
                queue.append(href['children'][child])
            members.extend(href['members'])
        return members

    @blueprint.route("/<uuid:organization>/view", methods=[ "GET" ])
    def get_groups(organization):
        return flask.jsonify({
            'status': True,
            'code': 200,
            'data': {
                'groups': database.get_groups_by_organization(organization),
                'hierarchy': database.get_group_hierarchy(organization)
            }
        })

    @blueprint.route("/<uuid:organization>/view/members", methods=[ "GET" ])
    @blueprint.route("/<uuid:organization>/<group>/view/members", methods=[ "GET" ])
    def get_group_members(organization, group=None):
        hierarchy = database.get_member_hierarchy(organization, group)
        print(hierarchy)
        return flask.jsonify({
            'status': True,
            'code': 200,
            'data': {
                'members': flatten_member_hierarchy(hierarchy),
                'hierarchy': hierarchy
            }
        })

    @blueprint.route("/join", methods=[ "POST" ])
    @auth.login_required
    def join_group():
        user = auth.current_user()
        role = auth.get_user_roles_callback(user)
        if role == 'admin':
            user_id = utils.get_field(flask.request, 'ID')
        else:
            user_id = user['ID']
        params = {
            'OID'            : utils.get_field(flask.request, 'OID'),
            'GName'          : utils.get_field(flask.request, 'group'),
            'ID'             : user_id
        }
        database.execute(( database.membership.insert(), params ))
        return flask.jsonify({
            "status": True,
            "code": 200,
            "data": params
        })

    @blueprint.route("/leave", methods=[ "POST" ])
    @auth.login_required
    def leave_group():
        user = auth.current_user()
        role = auth.get_user_roles_callback(user)
        if role == 'admin':
            user_id = utils.get_field(flask.request, 'ID')
        else:
            user_id = user['ID']
        params = {
            'OID'            : utils.get_field(flask.request, 'OID'),
            'GName'          : utils.get_field(flask.request, 'group'),
            'ID'             : user_id
        }
        database.execute(( database.membership.delete().where(
            (database.membership.c.OID == sql.bindparam('OID')) &\
            (database.membership.c.GName == sql.bindparam('GName')) &\
            (database.membership.c.ID == sql.bindparam('ID'))
        ), params ))
        return flask.jsonify({
            "status": True,
            "code": 200,
            "data": params
        })

    @blueprint.route("/create", methods=[ "POST" ])
    @auth.login_required(role = 'admin')
    def create_group():
        params = {
            'Name'         : utils.get_field(flask.request, 'name'),
            'OID'          : utils.get_field(flask.request, 'organization'),
            'Creator'      : auth.current_user()['ID'],
        }
        parent = utils.get_field(flask.request, 'parent', allow_null=True)

        queries = [ ( database.group.insert(), params ) ]
        if parent:
            gh_params = {
                'Name': params['name'],
                'Parent': parent,
                'OID': params['OID']
            }
            queries.append(( database.group_hierarchy.insert(), gh_params ))

        database.execute(*queries)

        return flask.jsonify({
            'status': True,
            'code': 200,
            'data': params
        }), 200

    return blueprint
