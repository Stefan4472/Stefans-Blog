import sys  
import pathlib
import click
import typing
import flask
from . import manage_util
from . import post_adder
from . import database_context


@flask.cli.with_appcontext
def reset_site():
    database_context.init_db()
    flask.current_app.search_engine.clear_all_data()
    flask.current_app.search_engine.commit()
    flask.current_app.manifest.clear()


@flask.cli.with_appcontext
def add_post(
        post_dir: pathlib.Path, 
        quiet: bool, 
):
    """Add post from the specified directory to the local site instance."""
    if not quiet:
        print('Adding post from directory "{}"'.format(post_dir))
    post_adder.add_post(
        post_dir,
        quiet,
    )


@flask.cli.with_appcontext
def add_posts(
        post_file_path: pathlib.Path,
        quiet: bool,
):
    print('Adding posts from {}'.format(post_file_path))
    try:
        with open(post_file_path, 'r') as post_file:
            for line in post_file:
                post_dir = pathlib.Path(line.strip())
                add_post(post_dir, quiet)
    except IOError as e:
        raise ValueError(str(e))


@flask.cli.with_appcontext
def push_to_production():
    """Push local site instance to the production server."""
    # TODO
    return


"""Click wrapper functions"""
@click.command('add_post')
@click.argument('post_dir')
@click.option('--quiet', is_flag=True, default=False, help='Whether to suppress print statements and confirmation prompts')
@flask.cli.with_appcontext
def add_post_command(
        post_dir: str, 
        quiet: bool, 
):
    """Add post from the specified directory to the local site instance."""
    try:
        post_dir = manage_util.resolve_directory_path(sys.argv[0], post_dir)
        add_post(post_dir, quiet)
    except ValueError as e:
        print('ERROR: {}'.format(e))
        sys.exit(1)


@click.command('add_posts')
@click.argument('post_file')
@click.option('--quiet', is_flag=True, default=False, help='Whether to suppress print statements and confirmation prompts')
@flask.cli.with_appcontext
def add_posts_command(
        post_file: str,
        quiet: bool,
):
    try:
        post_file_path = manage_util.resolve_file_path(sys.argv[0], post_file)
        add_posts(post_file_path, quiet)
    except ValueError as e:
        print('ERROR: {}'.format(e))
        sys.exit(1)


@click.command('reset_site')
@flask.cli.with_appcontext
def reset_site_command():
    """Resets the site. This includes the database, search index, and manifest."""
    reset_site()
