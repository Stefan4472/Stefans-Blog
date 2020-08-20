from flask import g, current_app
import flaskr.database as db
"""A few functions for accessing the database from the request context, "g"."""


def get_db():
    """Add database connection to the request object, `g`."""
    if 'db' not in g:
        # Create database if not exists
        g.db = db.Database(current_app.config['DATABASE_PATH'])

    return g.db


def close_db(e=None):
    """Close the database connection attached to the request object, `g`."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """Initialize the database instance."""
    db = get_db()
    with current_app.open_resource('posts_schema.sql') as f:
        db.run_script(f.read().decode('utf8'))