import base64
import typing

from flask import abort, current_app, redirect, request, url_for
from flask_login import LoginManager, UserMixin
from stefan_on_software.models.user import User
from werkzeug.security import check_password_hash

"""
Functionality for API authentication.

You must initialize `login_manager` on app start!
`login_manager.init_app()`
"""
login_manager = LoginManager()
login_manager.login_view = "blog.login"


def verify_login(email: str, password: str) -> User:
    # Ensure user exists and check password
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        current_app.logger.info(f"Verification failed for email={email}")
        raise ValueError("Invalid email or password")
    return user


@login_manager.unauthorized_handler
def unauthorized():
    # Redirect to login page for web requests
    if request.blueprint == "internal":
        return redirect(url_for("blog.login"))
    # Abort API requests
    abort(403)


@login_manager.request_loader
def request_loader(request) -> typing.Optional[UserMixin]:
    """
    Handles verification of API requests via HTTP Basic Authentication.

    The request must contain an 'Authorization' header. The value of the
    header should be the "[email]:[password]" of the user making the
    request.
    """
    if "Authorization" not in request.headers:
        return None
    if not request.headers["Authorization"].startswith("Basic "):
        return None
    # Decode base-64, then decode the resulting bytes to a string
    auth_string = base64.b64decode(request.headers["Authorization"][6:]).decode()
    if ":" not in auth_string:
        return None
    colon_index = auth_string.index(":")
    email = auth_string[:colon_index]
    password = auth_string[colon_index + 1 :]
    try:
        return verify_login(email, password)
    except ValueError:
        return None


@login_manager.user_loader
def user_loader(user_id: str):
    """
    Handles verification of session keys (made via website).

    Retrieves user based on user_id.
    """
    return User.query.get(int(user_id))
