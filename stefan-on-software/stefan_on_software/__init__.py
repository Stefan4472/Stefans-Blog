import os

import flask
import datetime
import copy
from stefan_on_software.site_config import ConfigKeys, SiteConfig
from stefansearch.engine.search_engine import SearchEngine

# Note: initialization order matters. db must be initialized first.
from .database import db


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
        app.logger.info(f"instance_path set to {app.instance_path}")
    if my_config.rel_static_path:
        # Set static path, if configured.
        # TODO: I'm not sure if this works 100% correctly. This needs to be tested.
        app.static_folder = os.path.join(app.root_path, my_config.rel_static_path)
        app.logger.info(f"static_folder set to {app.static_folder}")

    # Set path for where the sitemap file should be stored.
    app.config[ConfigKeys.SITEMAP_PATH] = os.path.join(app.static_folder, "sitemap.xml")

    from . import auth, cli, defaults

    # Populate app.config with paths that are set by default
    app.config.update(defaults.make_defaults(app.instance_path))

    # Init extensions
    auth.login_manager.init_app(app)
    db.init_app(app)

    from stefan_on_software.api import (
        commands_api,
        emails_api,
        files_api,
        posts_api,
        tags_api,
    )
    from stefan_on_software.views import internal_views, public_views

    # Register blueprints
    app.register_blueprint(public_views.BLUEPRINT)
    app.register_blueprint(internal_views.BLUEPRINT)
    app.register_blueprint(posts_api.BLUEPRINT)
    app.register_blueprint(tags_api.BLUEPRINT)
    app.register_blueprint(files_api.BLUEPRINT)
    app.register_blueprint(commands_api.BLUEPRINT)
    app.register_blueprint(emails_api.BLUEPRINT)
    app.add_url_rule("/", endpoint="index")

    # Init search engine
    app.search_engine = SearchEngine(app.config[ConfigKeys.SEARCH_INDEX_PATH])

    # Register click commands
    app.cli.add_command(cli.init_site)
    app.cli.add_command(cli.delete_site)
    app.cli.add_command(cli.add_user)

    @app.template_filter('iso8601')
    def _jinja2_format_datetime_iso8601(dt: datetime.datetime) -> str:
        """Format the given datetime in ISO8601 with UTC timezone."""
        dt_copy = copy.copy(dt)
        dt_copy.replace(microsecond=0).replace(tzinfo=datetime.timezone.utc)
        return dt_copy.isoformat()

    return app
