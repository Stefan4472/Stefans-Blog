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
        TEST_THING=1000,
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import database
    database.init_app(app)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    #from .search_engine.index import Index
    # TODO: PROPERLY INIT THE SEARCH ENGINE

    return app
