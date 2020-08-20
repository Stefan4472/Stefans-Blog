import os
import sys
import click
import flask
import pathlib
from . import database_context
from . import blog
from . import manifest as mn
from . import manage_blog
from .search_engine import index 


def create_app():
    # create and configure the app
    app = flask.Flask(__name__, instance_relative_config=True)
    # TODO: MAKE INTO PATHLIB OBJECTS?
    app.config.from_mapping(
        DATABASE_PATH=os.path.join(app.instance_path, 'posts.db'),
        SITE_LOG_PATH=os.path.join(app.instance_path, 'sitelog.txt'),
        FEATURED_POSTS_PATH=os.path.join(app.instance_path, 'featured_posts.txt'),
        SEARCH_INDEX_PATH=os.path.join(app.instance_path, 'index.json'),
        SECRET_PATH=os.path.join(app.instance_path, 'secret.txt'),  # YES I KNOW THIS SHOULDN'T BE PLAIN TEXT
        MANIFEST_PATH=os.path.join(app.instance_path, 'manifest.json'),
    )

    # Create the instance folder if it doesn't already exist
    pathlib.Path(app.instance_path).mkdir(exist_ok=True)

    # Initialize and return app
    init_app(app)
    return app


def init_app(flask_app):
    """Perform any initialization for the provided Flask app instance."""
    flask_app.teardown_appcontext(database_context.close_db)
    flask_app.cli.add_command(manage_blog.reset_site_command)
    flask_app.cli.add_command(manage_blog.add_post_command)
    flask_app.cli.add_command(manage_blog.add_posts_command)
    
    # Register blueprint
    flask_app.register_blueprint(blog.bp)
    flask_app.add_url_rule('/', endpoint='index')

    # Init search engine and manifest
    flask_app.search_engine = index.connect(flask_app.config['SEARCH_INDEX_PATH'])
    flask_app.manifest = mn.Manifest(flask_app.config['MANIFEST_PATH'])



