import uuid
import string
import secrets

import flask
from sqlalchemy import sql
from werkzeug import exceptions

from .. import utils

def create_blueprint(auth, tokens, database):
    blueprint = flask.Blueprint(
        "organization", __name__,
        template_folder="templates",
        url_prefix="/organization"
    )

    @blueprint.route("/verify", methods=[ "POST" ])
    def verify_org_code():
        query = sql.select([ database.organization ]).where(sql.and_(
            database.organization.c.Code == sql.bindparam('code'),
            database.organization.c.Name == sql.bindparam('name')
        ))
        params = {
            'code': utils.get_field(flask.request, 'code'),
            'name': utils.get_field(flask.request, 'name')
        }
        result = database.execute(( query, params ))[0]
        result = result.fetchone()
        if not result:
            raise exceptions.BadRequest("Specified organization does not exist")

        return flask.jsonify({
            'status': True,
            'code': 200,
            'data': { **result }
        }), 200

    @blueprint.route("/create", methods=[ "POST" ])
    def create_organization():
        query = sql.select([ database.organization.c.OID ]).where(
            database.organization.c.Code == sql.bindparam('code')
        )
        
        while True:
            org_code = ''.join(
                secrets.choice(string.ascii_uppercase + string.digits)
                for _ in range(6)
            )
            result = database.execute(( query, { 'code': org_code } ))[0]
            result = result.fetchone()
            if not result: break

        params = {
            'OID'          : str(uuid.uuid4()),
            'Name'         : utils.get_field(flask.request, 'name'),
            'Address'      : utils.get_field(flask.request, 'address'     , allow_null=True),
            'Website'      : utils.get_field(flask.request, 'website'     , allow_null=True),
            'Code'         : org_code
        }

        database.execute((database.organization.insert(), params))

        return flask.jsonify({
            'status': True,
            'code': 200,
            'data': params
        }), 200



    return blueprint
    