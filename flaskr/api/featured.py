import flask
from flask import request, Response, current_app
from flask_login import login_required
from flaskr.database import db
from flaskr.models.post import Post
from flaskr import util


# Blueprint under which all views will be assigned
BLUEPRINT = flask.Blueprint('featured', __name__, url_prefix='/api/v1/featured')


@BLUEPRINT.route('/', methods=['GET'])
@login_required
def get_posts():
    """Get list of featured posts (slugs)."""
    query = Post.query.filter(Post.is_featured)
    return flask.jsonify([post.slug for post in query.all()])
