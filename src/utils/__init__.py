from werkzeug import exceptions

from . import qrcode
from . import database

__version__ = "1.0"
__all__     = [ "qrcode", "database" ]

def get_field(request, key, allow_null=False):
    """ Checks for the presence of the given key in the request params, and raises a
    BadRequest exception in case the parameter is missing.

    Args:
        request (flask.Request): The request received on the server.
        key (str): The key to retrieve.
        allow_null (boolean): Only check for key presence, and not whether the value is usable.
    """
    try:
        value = request.form[key]
        if not allow_null and not value:
            raise KeyError()
    except KeyError as exc:
        try:
            value = request.args[key]
            if not allow_null and not value:
                raise KeyError() from exc
        except KeyError as exc2:
            if allow_null: return None
            raise exceptions.BadRequest(
                f"Missing {key} field in the request"
            ) from exc2
    return value