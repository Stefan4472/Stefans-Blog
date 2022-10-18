import flask
import pathlib
from .database import db
from flaskr.views import public_views, internal_views
from flaskr.api import post_api, featured_api, image_api, file_api, email_api, tags_api
from . import auth
from . import config as cfg
from . import cli
from stefansearch.engine.search_engine import SearchEngine


def create_app(config: cfg.Config = None):
    """Create and configure the Flask app."""
    app = flask.Flask(__name__)

    # Use provided config or load from environment variables
    my_config = config if config else cfg.Config.load_from_env()
    my_config.check_validity()
    app.config.update(my_config.to_dict())

    # Create the instance folder if it doesn't already exist
    instance_path = pathlib.Path(app.instance_path)
    instance_path.mkdir(exist_ok=True)

    # Init extensions
    auth.login_manager.init_app(app)
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(public_views.BLUEPRINT)
    app.register_blueprint(internal_views.BLUEPRINT)
    app.register_blueprint(post_api.BLUEPRINT)
    app.register_blueprint(featured_api.BLUEPRINT)
    app.register_blueprint(tags_api.BLUEPRINT)
    app.register_blueprint(image_api.BLUEPRINT)
    app.register_blueprint(file_api.BLUEPRINT)
    app.register_blueprint(email_api.BLUEPRINT)
    app.add_url_rule('/', endpoint='index')

    # Init search engine
    app.search_engine = SearchEngine(app.config[cfg.Keys.SEARCH_INDEX_PATH])

    # Register click commands
    app.cli.add_command(cli.reset_site)
    app.cli.add_command(cli.add_user)

    return app
