import uuid
import time
import string
import base64
import secrets
import datetime

import flask
import bcrypt
import isodate

def modify_date(date, *args, **kwargs):
    return date + datetime.timedelta(*args, **kwargs)

def format_date(date, fmtstr):
    return date.strftime(fmtstr)

def parse_date(datestr):
    if not datestr: return datetime.datetime.now()
    try:
        return isodate.parse_datetime(datestr)
    except isodate.ISO8601Error:
        return datetime.datetime.combine(
            isodate.parse_date(datestr), datetime.time.min
        )

def parse_time(timestr):
    return isodate.parse_time(timestr)

def current_time():
    return datetime.datetime.now().time()

class CodeGenerator:
    """ Defines an abstraction that generates assured unique codes
        using a generator function, by remembering previously
        generated values. """
    def __default_generator(self, length = 6):
        return ''.join(
            secrets.choice(string.ascii_uppercase + string.digits)
            for _ in range(length)
        )

    def __init__(self, codes = None, gen_fx = None):
        self.__codes = codes or []
        self.__generator = gen_fx or self.__default_generator

    def generate(self, *args, **kwargs):
        """ Generates a unique code using the generator function. """
        while True:
            value = self.__generator(*args, **kwargs)
            if value not in self.__codes:
                self.__codes.append(value); break
        return value

def make_token(username: str, user_id: str):
    """ Generate a seemingly safe to use secure token. """
    ids = uuid.uuid4(), uuid.uuid1()
    token = base64.urlsafe_b64encode(
        username.encode() + b':'
        + ids[0].bytes + b':' + ids[1].bytes
    ).decode('ascii') + secrets.token_urlsafe(10)
    data = {
        'username': username,
        'ID': user_id,
        'timestamp': int(time.time())
    }
    return token, data

def hash_password(password):
    """ Hash a password with added salt using bcrypt and return the
        base64 encoded version of the hash and the bytes """
    salt = bcrypt.gensalt()
    hashed_pw = bcrypt.hashpw(password.encode(), salt)
    return (
        base64.b64encode(hashed_pw).decode('ascii'),
        base64.b64encode(salt).decode('ascii')
    )

def verify_password(password, hashed_pw):
    """ Verify a given password against a base 64 encoded password returned
        by a previous call to `utils.hash_password` """
    password_hash = base64.b64decode(hashed_pw)
    return bcrypt.checkpw(password.encode(), password_hash)

def new_uuid():
    return str(uuid.uuid4())

def get_field(request, key, allow_null=False):
    """ Checks for the presence of the given key in the request params, and raises a
        BadRequest exception in case the parameter is missing.

    Args:
        request (flask.Request): The request received on the server.
        key (str): The key to retrieve.
        allow_null (boolean): Only check for key presence, and not whether the value is usable.
    """
    try:
        form_params = request.form.to_dict(flat=False)
        value = form_params[key]
        if len(value) == 1: value = value[0]
        if not allow_null and not value:
            raise KeyError()
    except KeyError as exc:
        try:
            arg_params = request.args.to_dict(flat=False)
            value = arg_params[key]
            if len(value) == 1: value = value[0]
            if not allow_null and not value:
                raise KeyError() from exc
        except KeyError:
            if allow_null: return None
            flask.abort(400, description=f"Missing {key} field in the request")
    return value

from . import qrcode
from . import database

__version__ = "1.0"
__all__     = [ "qrcode", "database" ]