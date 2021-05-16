import sys  
import pathlib
import click
import flask
import timeit
from . import manage_util
from . import models
from . import post_adder
from . import post_uploader
from .database import db


@flask.cli.with_appcontext
def reset_site():
    """Reset all post data. Includes the database, search index, and manifest."""
    db.drop_all()
    db.create_all()
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
def push_to_remote_command(quiet: bool):
    """Syncs the local site instance to the production server."""
    start = timeit.default_timer()
    # Call the `push_to_remote()` function
    push_to_remote()
    end = timeit.default_timer()
    if not quiet:
        print('Completed in {} seconds'.format(end - start))


@click.command('featured')
@flask.cli.with_appcontext
def print_featured_posts_command():
    """List the featured posts."""
    for post in models.Post.query.filter(models.Post.is_featured).all():
        click.echo(post.slug)


@click.command('feature_post')
@click.argument('slug')
@click.option('--featured', type=bool, default=True)
@flask.cli.with_appcontext
def feature_post_command(
        slug: str,
        featured: bool,
):
    """Sets the post with specified slug to be featured."""
    post = models.Post.query.filter_by(slug=slug).first()
    if post:
        post.is_featured = featured
        db.session.commit()
    else:
        click.echo('No post with specified slug')
