import flask
import pathlib
from .database import db
from . import views
from . import config as cfg
from . import manage_blog
from . import manifest as mn
from simplesearch.searchengine import SearchEngine


def create_app():
    """Create and configure the Flask app."""
    app = flask.Flask(__name__)

    # Create the instance folder if it doesn't already exist
    instance_path = pathlib.Path(app.instance_path)
    instance_path.mkdir(exist_ok=True)

    # Load config variables
    app.config.from_object(cfg.Config.load_from_env(instance_path))

    # Init SQL Alchemy
    db.init_app(app)

    # Register blueprint
    # Note: we import `blog` here to avoid a circular import on `models`
    app.register_blueprint(views.BLUEPRINT)
    app.add_url_rule('/', endpoint='index')

    # Init search engine and manifest
    app.search_engine = SearchEngine(app.config['SEARCH_INDEX_PATH'])
    app.manifest = mn.Manifest(app.config['MANIFEST_PATH'])

    # Register click commands
    app.cli.add_command(manage_blog.reset_site_command)
    app.cli.add_command(manage_blog.add_post_command)
    app.cli.add_command(manage_blog.add_posts_command)
    app.cli.add_command(manage_blog.push_to_remote_command)
    app.cli.add_command(manage_blog.print_featured_posts_command)
    app.cli.add_command(manage_blog.feature_post_command)

    return app
