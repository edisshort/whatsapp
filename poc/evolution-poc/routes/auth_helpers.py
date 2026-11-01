from functools import wraps

from flask import redirect, session, url_for

from config import Config


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped


def check_login(username: str, password: str) -> bool:
    return username == Config.ADMIN_USERNAME and password == Config.ADMIN_PASSWORD
