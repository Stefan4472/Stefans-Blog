import os
import sys
import click
import flask
import pathlib
import json
from . import database_context
from . import blog
from . import manifest as mn
from . import manage_blog
from simplesearch.searchengine import SearchEngine


def create_app():
    """Create and configure the Flask app."""
    app = flask.Flask(__name__, instance_relative_config=True)

    # YES I KNOW THIS SHOULDN'T BE PLAIN TEXT
    secret_path = os.path.join(app.instance_path, 'secret.json')
    with open(secret_path, 'r') as secret_file:
        secret_data = json.load(secret_file)
        # TODO: MAKE SURE ALL VALUES HAVE BEEN SET
    
    # TODO: MAKE INTO PATHLIB OBJECTS?
    app.config.from_mapping(
        DATABASE_PATH=os.path.join(app.instance_path, 'posts.db'),
        SITE_LOG_PATH=os.path.join(app.instance_path, 'sitelog.txt'),
        FEATURED_POSTS_PATH=os.path.join(app.instance_path, 'featured_posts.txt'),
        SEARCH_INDEX_PATH=os.path.join(app.instance_path, 'index.json'),
        MANIFEST_PATH=os.path.join(app.instance_path, 'manifest.json'),
        SECRET_PATH=secret_path,
        SECRET_VALS=secret_data,
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
    flask_app.cli.add_command(manage_blog.push_to_remote_command)
    
    # Register blueprint
    flask_app.register_blueprint(blog.bp)
    flask_app.add_url_rule('/', endpoint='index')

    # Init search engine and manifest
    flask_app.search_engine = SearchEngine(pathlib.Path(flask_app.config['SEARCH_INDEX_PATH']))
    flask_app.manifest = mn.Manifest(flask_app.config['MANIFEST_PATH'])



