import flask
import os
from pathlib import Path
from .database import db
from flaskr.views import public_views, internal_views
from flaskr.api import post_api, featured_api, image_api, file_api, email_api, tags_api
from flaskr.site_config import SiteConfig, ConfigKeys
from . import auth
from . import cli
from . import defaults
from stefansearch.engine.search_engine import SearchEngine


def create_app(config: SiteConfig = None):
    """Create and configure the Flask app."""
    app = flask.Flask(__name__)
    # Use provided config or load from environment variables
    my_config = config if config else SiteConfig.load_from_env()
    my_config.check_validity()
    app.config.update(my_config.to_dict())

    if my_config.rel_instance_path:
        # Set instance path, if configured.
        # https://flask.palletsprojects.com/en/2.2.x/config/#instance-folders
        app.instance_path = os.path.join(app.root_path, my_config.rel_instance_path)
        app.logger.info(f'instance_path set to {app.instance_path}')
    if my_config.rel_static_path:
        # Set static path, if configured.
        # TODO: I'm not sure if this works 100% correctly. This needs to be tested.
        app.static_folder = os.path.join(app.root_path, my_config.rel_static_path)
        app.logger.info(f'static_folder set to {app.static_folder}')

    # Populate app.config with paths that are set by default
    app.config.update(defaults.make_defaults(app.instance_path))

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
    app.search_engine = SearchEngine(app.config[ConfigKeys.SEARCH_INDEX_PATH])

    # Register click commands
    app.cli.add_command(cli.init_site)
    app.cli.add_command(cli.delete_site)
    app.cli.add_command(cli.add_user)

    return app
