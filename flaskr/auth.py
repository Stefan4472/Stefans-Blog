import typing
from flask import current_app, request, redirect, url_for, abort
from flask_login import LoginManager, UserMixin
from flaskr.models.user import User
from flaskr.config import Keys
'''
Functionality for API authentication.

You must initialize `login_manager` on app start!
`login_manager.init_app()`
'''
login_manager = LoginManager()
login_manager.login_view = 'blog.login'


@login_manager.unauthorized_handler
def unauthorized():
    # Redirect to login page for web requests
    if request.blueprint == 'internal':
        return redirect(url_for('blog.login'))
    # Abort API requests
    abort(403)


@login_manager.request_loader
def request_loader(request) -> typing.Optional[UserMixin]:
    """
    Handles verification of API requests.

    Verify that the 'Authorization' header equals our secret key.
    Returns an empty `UserMixin` on success.

    Docs: https://flask-login.readthedocs.io/en/latest/#installation
    Example: http://gouthamanbalaraman.com/blog/minimal-flask-login-example.html
    """
    token = str(request.headers.get('Authorization'))
    secret = str(current_app.config[Keys.SECRET_KEY])
    return UserMixin() if token == secret else None


@login_manager.user_loader
def user_loader(user_id: str):
    """
    Handles verification of session keys (made via website).

    Retrieves user based on user_id.
    """
    return User.query.get(int(user_id))
