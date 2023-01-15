import os
import shutil

import click
import flask
from flask import current_app
from werkzeug.security import generate_password_hash

from .database import db

# Ensure all SQLAlchemy models are imported for db.create_all()
from .models.file import File
from .models.post import Post
from .models.tag import Tag
from .models.user import User
from .site_config import ConfigKeys

# TODO: a 'cleanup()' function that deletes all file uploads that are no longer used -- i.e., not registered in the database and with 0 references


@click.command("init_site")
@flask.cli.with_appcontext
def init_site():
    """
    Creates site instance and static folders, along with the default file
    structure and database.
    """
    # Create the instance folder
    try:
        os.mkdir(current_app.instance_path)
    except FileExistsError:
        raise ValueError(f"Can't create site. Delete {current_app.instance_path} first")
    # Create the static folder
    try:
        os.mkdir(current_app.static_folder)
    except FileExistsError:
        raise ValueError(f"Can't create site. Delete {current_app.static_folder} first")

    # Create and initialize the database
    db.create_all()
    # Create other necessary files
    open(current_app.config[ConfigKeys.TRAFFIC_LOG_PATH], "w+").close()
    with open(current_app.config[ConfigKeys.SEARCH_INDEX_PATH], "w+") as f:
        # TODO: search engine needs to be fixed to allow empty files
        f.write('{"index": {}, "doc_data": {}}')
    click.echo("Created site")


@click.command("delete_site")
@flask.cli.with_appcontext
def delete_site():
    """Deletes instance and static folders."""
    shutil.rmtree(current_app.instance_path)
    shutil.rmtree(current_app.static_folder)
    click.echo("Deleted site")


@click.command("add_user")
@click.argument("name")
@click.argument("email")
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
        raise click.ClickException("A user with the given email address already exists")
    # Create new user and add to database
    user = User(
        email=email,
        password=generate_password_hash(password, method="sha256"),
        name=name,
    )
    db.session.add(user)
    db.session.commit()
    click.echo("Created user")
