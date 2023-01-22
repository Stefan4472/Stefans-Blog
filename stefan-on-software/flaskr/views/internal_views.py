import flask
from flask_login import current_user, login_required, logout_user

BLUEPRINT = flask.Blueprint("internal", __name__)


@BLUEPRINT.route("/landing")
@login_required
def landing():
    return f"<p>Welcome, {current_user.name}</p>"


@BLUEPRINT.route("/logout")
@login_required
def logout():
    logout_user()
    return flask.redirect(flask.url_for("blog.index"))
