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
from . import config as cfg
from simplesearch.searchengine import SearchEngine


def create_app():
    """Create and configure the Flask app."""
    app = flask.Flask(__name__, instance_relative_config=True)

    # Create the instance folder if it doesn't already exist
    instance_path = pathlib.Path(app.instance_path)
    instance_path.mkdir(exist_ok=True)

    print(cfg.Config.load_from_env(instance_path))
    app.config.from_object(cfg.Config.load_from_env(instance_path))

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
    flask_app.search_engine = SearchEngine(flask_app.config['SEARCH_INDEX_PATH'])
    flask_app.manifest = mn.Manifest(flask_app.config['MANIFEST_PATH'])
