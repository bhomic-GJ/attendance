import uuid
import string
import secrets

import flask
from sqlalchemy import sql, exc
from werkzeug import exceptions

from .. import utils

def create_blueprint(auth, tokens, database):
    blueprint = flask.Blueprint(
        "group", __name__,
        template_folder="templates",
        url_prefix="/group"
    )

    hierarchy_query = sql.select([ database.group_hierarchy.c.Parent ]).where(sql.and_(
        database.group_hierarchy.c.Name == sql.bindparam('name'),
        database.group_hierarchy.c.OID  == sql.bindparam('OID'),
    )).limit(1)

    def get_parent(name, organization):
        result = database.execute(( hierarchy_query, dict(name=name, OID=organization) ))[0]
        result = result.fetchone()
        if not result: raise ValueError("Invalid group specified")
        return result['Parent'], organization

    def get_hierarchy(name, organization):
        hierarchy = []
        data = (name, organization)
        while True:
            hierarchy.append(data)
            data = get_parent(*data)
            if not data[0]: break
        return hierarchy

    @blueprint.route("/create", methods=[ "POST" ])
    @auth.login_required(role = 'admin')
    def create_group():
        params = {
            'Name'         : utils.get_field(flask.request, 'name'),
            'OID'          : utils.get_field(flask.request, 'organization'),
            'Creator'      : auth.current_user()['ID'],
            'Creation_Date': None
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
    