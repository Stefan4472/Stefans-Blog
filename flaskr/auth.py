import typing
from flask import current_app
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


# @login_manager.request_loader
# def load_user(request) -> typing.Optional[UserMixin]:
#     """
#     Verify that the 'Authorization' header equals our secret key.
#     Returns an empty `UserMixin` on success.
#
#     Docs: https://flask-login.readthedocs.io/en/latest/#installation
#     Example: http://gouthamanbalaraman.com/blog/minimal-flask-login-example.html
#     """
#     print('Loading user via request loader')
#     token = str(request.headers.get('Authorization'))
#     secret = str(current_app.config[Keys.SECRET_KEY])
#     return UserMixin() if token == secret else None


@login_manager.user_loader
def load_user(user_id: str):
    """Retrieve user based on user_id."""
    print('Loading user via user loader')
    return User.query.get(int(user_id))
