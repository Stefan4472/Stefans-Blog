import click
import flask
import sys
from werkzeug.security import generate_password_hash
from .database import db

# Ensure all SQLAlchemy models are imported for db.create_all()
from .models.file import File
from .models.image import Image
from .models.post import Post
from .models.tag import Tag
from .models.user import User


@click.command('reset_site')
@flask.cli.with_appcontext
def reset_site():
    """Reset all post data. Includes the database, search index, and manifest."""
    db.drop_all()
    db.create_all()
    flask.current_app.search_engine.clear_all_data()
    flask.current_app.search_engine.commit()
    click.echo('Reset site')


@click.command('add_user')
@click.argument('name')
@click.argument('email')
@click.password_option(required=True)
@flask.cli.with_appcontext
def add_user(
        name: str,
        email: str,
        password: str,
):
    """
    Adds a user to the database so that they can login to the site.

    NAME: full name
    EMAIL: email address
    PASSWORD: password that will be used to login
    """
    if User.query.filter_by(email=email).first():
        raise click.ClickException('A user with the given email address already exists')
    # Create new user and add to database
    user = User(
        email=email,
        password=generate_password_hash(password, method='sha256'),
        name=name,
    )
    db.session.add(user)
    db.session.commit()
    click.echo('Created user')
