from flask import redirect, session
from functools import wraps


def login_required(f):
    """Decorates an app path that needs login information."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return wrapper