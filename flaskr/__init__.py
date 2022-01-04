import flask
import pathlib
from .database import db
from flaskr.views import public_views
from flaskr.api import post_api, featured_api, image_api
from . import auth
from . import config as cfg
from . import cli
from simplesearch.searchengine import SearchEngine


def create_app():
    """Create and configure the Flask app."""
    app = flask.Flask(__name__)
    auth.login_manager.init_app(app)

    # Create the instance folder if it doesn't already exist
    instance_path = pathlib.Path(app.instance_path)
    instance_path.mkdir(exist_ok=True)

    # Load config variables
    app.config.from_object(cfg.Config.load_from_env(instance_path))

    # Init SQL Alchemy
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(public_views.BLUEPRINT)
    app.register_blueprint(post_api.BLUEPRINT)
    app.register_blueprint(featured_api.BLUEPRINT)
    app.register_blueprint(image_api.BLUEPRINT)
    app.add_url_rule('/', endpoint='index')

    # Init search engine and manifest
    app.search_engine = SearchEngine(app.config['SEARCH_INDEX_PATH'])

    # Register click commands
    app.cli.add_command(cli.reset_site)

    return app
