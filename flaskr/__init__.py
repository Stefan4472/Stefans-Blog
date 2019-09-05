import os
from flask import Flask

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'posts.db'),
        VISIT_LOG=os.path.join(app.instance_path, 'sitelog.txt'),
        FEATURED_POSTS_FILE=os.path.join(app.instance_path, 'featured_posts.txt'),
        SEARCH_INDEX_FILE=os.path.join(app.instance_path, 'index.json'),
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

    # Init database 
    from . import database
    database.init_app(app)

    # Init blueprint
    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    # Init search engine instance and attach it to the 'app' object
    from .search_engine.index import restore_index_from_file
    app.search_engine = restore_index_from_file(app.config['SEARCH_INDEX_FILE'])

    return app
