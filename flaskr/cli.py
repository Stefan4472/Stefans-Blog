import click
import flask
from .database import db


@click.command('reset_site')
@flask.cli.with_appcontext
def reset_site():
    """Reset all post data. Includes the database, search index, and manifest."""
    db.drop_all()
    db.create_all()
    flask.current_app.search_engine.clear_all_data()
    flask.current_app.search_engine.commit()
