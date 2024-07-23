from functools import wraps
from flask import request, redirect, url_for, make_response
from models.utils import Auth
from models.database.db_utils import DbInputStream
from os import getenv
db = DbInputStream('mysql-app', int(getenv("DB_PORT")), getenv("DB_ID"), getenv("DB_PSWD"))

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_token = request.cookies.get('SESSID', default=None)
            usr_id = Auth.is_auth(auth_token, db)

            if usr_id is None:
                return redirect(url_for('login'))

            if not has_role(usr_id, role):
                return make_response("UNAUTHORIZED", 401)

            return f(*args, **kwargs)
        return decorated_function
    return decorator

def has_role(usr_id, role):
    if role == 'admin':
        return Auth.is_admin(usr_id, db)
    elif role == 'super_admin':
        return Auth.is_super_admin(usr_id, db)
    # Ajoutez d'autres rôles ici si nécessaire
    return False
