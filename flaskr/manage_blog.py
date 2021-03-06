import sys  
import pathlib
import click
import typing
import flask
import timeit
from . import manage_util
from . import post_adder
from . import post_uploader
from . import database_context


@flask.cli.with_appcontext
def reset_site():
    """Reset all post data. Includes the database, search index, and manifest."""
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
    """Adds all posts from the specified file.

    The file should consist of one absolute path per line.
    """
    if not quiet:
        print('Adding posts from {}'.format(post_file_path))
    try:
        with open(post_file_path, 'r') as post_file:
            for line in post_file:
                post_dir = pathlib.Path(line.strip())
                add_post(post_dir, quiet)
    except IOError as e:
        raise ValueError(str(e))


@flask.cli.with_appcontext
def push_to_remote():
    """Push local site instance to the production server."""
    print('Pushing to production')
    post_uploader.push_to_remote(False)


"""Click wrapper functions"""
@click.command('add_post')
@click.argument('post_dir')
@click.option('--quiet', is_flag=True, default=False, help='Whether to suppress print statements and confirmation prompts')
def add_post_command(
        post_dir: str, 
        quiet: bool, 
):
    """Add post from the specified directory to the local site instance."""
    try:
        post_dir = manage_util.resolve_directory_path(sys.argv[0], post_dir)
        start = timeit.default_timer()
        # Call the `add_post` function
        add_post(post_dir, quiet)
        end = timeit.default_timer()
        if not quiet:
            print('Completed in {} seconds'.format(end - start))
    except ValueError as e:
        print('ERROR: {}'.format(e))
        sys.exit(1)


@click.command('add_posts')
@click.argument('post_file')
@click.option('--quiet', is_flag=True, default=False, help='Whether to suppress print statements and confirmation prompts')
def add_posts_command(
        post_file: str,
        quiet: bool,
):
    post_file_path = manage_util.resolve_file_path(sys.argv[0], post_file)
    start = timeit.default_timer()
    # Call the `add_posts` function
    add_posts(post_file_path, quiet)
    end = timeit.default_timer()
    if not quiet:
        print('Completed in {} seconds'.format(end - start))


@click.command('reset_site')
def reset_site_command():
    """Resets the site. This includes the database, search index, and manifest."""
    reset_site()


@click.command('push')
@click.option('--quiet', is_flag=True, default=False, help='Whether to suppress print statements and confirmation prompts')
def push_to_remote_command(
        quiet: bool
):
    """Syncs the local site instance to the production server."""
    start = timeit.default_timer()
    # Call the `push_to_remote()` function
    push_to_remote()
    end = timeit.default_timer()
    if not quiet:
        print('Completed in {} seconds'.format(end - start))
            