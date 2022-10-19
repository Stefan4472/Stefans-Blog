import flask
import os
from pathlib import Path
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

    if my_config.rel_instance_path:
        # Set instance path, if configured.
        # https://flask.palletsprojects.com/en/2.2.x/config/#instance-folders
        app.instance_path = os.path.join(app.root_path, my_config.rel_instance_path)
        app.logger.info(f'instance_path set to {app.instance_path}')
    if my_config.rel_static_path:
        # Set static path, if configured.
        # See https://stackoverflow.com/a/45623197
        # app.static_url_path = '/' + my_config.rel_static_path
        # TODO: I'm not sure if this works 100% correctly. This needs to be tested.
        app.static_folder = os.path.join(app.root_path, my_config.rel_static_path)
        app.logger.info(f'static_folder set to {app.static_folder}')
        app.logger.info(f'static_url_path set to {app.static_url_path}')

    # Create the instance folder if it doesn't already exist
    instance_path = Path(app.instance_path)
    instance_path.mkdir(exist_ok=True)
    # Create the static folder if it doesn't already exist
    static_path = Path(app.static_folder)
    static_path.mkdir(exist_ok=True)

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
