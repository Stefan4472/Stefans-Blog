import os
import sys
import click
from flask import Flask, current_app, g
from flask.cli import with_appcontext
from . import database
from . import blog
from .search_engine import index 
from .manage_blog import add_post, upload_posts

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        DATABASE_PATH=os.path.join(app.instance_path, 'posts.db'),
        SITE_LOG_PATH=os.path.join(app.instance_path, 'sitelog.txt'),
        FEATURED_POSTS_PATH=os.path.join(app.instance_path, 'featured_posts.txt'),
        SEARCH_INDEX_PATH=os.path.join(app.instance_path, 'index.json'),
        SECRET_PATH=os.path.join(app.instance_path, 'secret.txt')  # YES I KNOW THIS SHOULDN'T BE PLAIN TEXT
    )

    # Load the instance config, if it exists, when not testing
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    # Load the test config if passed in
    else:
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    #
    init_app(app)

    # Register blueprint
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    # Init search engine instance and attach it to the 'app' object
    app.search_engine = index.connect(app.config['SEARCH_INDEX_PATH'])

    return app

# registers the Database teardown method, close_db()
def init_app(app):
    app.teardown_appcontext(database.close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(init_search_index_command)
    app.cli.add_command(add_post)
    app.cli.add_command(upload_posts)

# command-line function to re-init the database to the
# original schema. Run using "flask init-db"
@click.command('init_db')
@with_appcontext
def init_db_command():
    database.init_db()
    click.echo('Initialized the database.')

@click.command('init_search_index')
@with_appcontext
def init_search_index_command():
    search_index = None
    if current_app.search_engine:
        search_index = current_app.search_engine
    else:
        search_index = index.connect(current_app.config['SEARCH_INDEX_FILE'])

    search_index.clear_all_data()
    search_index.commit()
    click.echo('Initialized the search engine index.')