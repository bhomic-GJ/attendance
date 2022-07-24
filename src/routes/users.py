import flask
from sqlalchemy import exc

from .. import utils
from . import login_required

def create_blueprint(auth, tokens, database, *args, **kwargs):
    blueprint = flask.Blueprint(
        'users', __name__,
        template_folder='templates',
        url_prefix='/user'
    )

    @blueprint.route("/")
    def current_user():
        current_user = auth.current_user() or flask.g.user
        if not current_user:
            return flask.redirect(flask.url_for("index"))
        return flask.redirect(
            flask.url_for("routes.users.user", user_id=current_user['ID'])
        )

    @blueprint.route("/<uuid:user_id>")
    def user(user_id):
        current_user = auth.current_user() or flask.g.user
        if current_user:
            current_user['role'] = database.get_user_role(current_user['ID'])
        user = database.get_user_by_id(user_id)
        organization = None
        if user:
            organization = database.get_organization_by_id(user['OID'])
        return flask.render_template(
            "ui/home_existing_user.html.jinja",
            user = user, organization = organization,
            current_user = current_user,
            orgs = database.get_organizations()
        )

    @blueprint.route("/edit")
    @login_required(auth)
    def edit_user():
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