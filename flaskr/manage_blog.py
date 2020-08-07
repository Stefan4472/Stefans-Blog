import sys  
import pathlib
import click
import typing
from flask import current_app#, url_for
from flask.cli import with_appcontext
import flaskr.manage_util as util
# from flaskr.database import Database
# import flaskr.search_engine.index as index  # TODO: BETTER IMPORTS
# from flaskr.manifest import Manifest
import flaskr.post_adder as post_adder

# TODO: ADD_POSTS_FROM_FILE

@click.command('add_post')
@click.argument('post_dir')
@click.option('--quiet', is_flag=True, default=False, help='Whether to suppress print statements and confirmation prompts')
@with_appcontext
def add_post(
        post_dir: str, 
        quiet: bool, 
):
    try:
        post_dir = util.resolve_directory_path(sys.argv[0], post_dir)
    except ValueError as e:
        print('ERROR: {}'.format(e))
        sys.exit(1)

    if not quiet:
        print('Adding post from directory "{}"'.format(post_dir))
    
    post_adder.PostAdder().add_post(
        post_dir,
        current_app.static_path,
        current_app.config['MANIFEST_PATH'],
        quiet,
    )

def push_to_production():
    # TODO
    return
