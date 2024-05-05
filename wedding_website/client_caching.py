from functools import wraps

from flask import make_response


def client_cached(f):  # type: ignore
    @wraps(f)
    def decorated_function(*args, **kwargs):  # type: ignore
        resp = make_response(f(*args, **kwargs))
        # Example: Cache for 24 hours
        resp.headers["Cache-Control"] = "max-age=86400, public"  # 24 hours
        return resp

    return decorated_function
