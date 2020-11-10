import pathlib
import typing
import flask
import pysftp
import json
import io
from flask import current_app
from . import manifest as mn
from . import manage_util as util


@flask.cli.with_appcontext
def push_to_remote(
        quiet: bool,
):
    """Performs the multi-step process of syncing the remote server 
    (URL, username and password defined in 'secret.json') with the local
    server.

    In order:
    - Lookup authentication data in the secret file
    - Connect to the remote server
    - Download the remote server's manifest
    - Calculate the diff between local manifest and server manifest
    - Perform necessary file writes and deletes

    SFTP instructions for PythonAnywhere: https://help.pythonanywhere.com/pages/SSHAccess
    """
    # Read the secret file to get host information
    try:
        with open(current_app.config['SECRET_PATH']) as secret_file:
            secret_data = json.load(secret_file)
            host = secret_data['host']
            username = secret_data['username']
            password = secret_data['password']
            remote_base_path = secret_data['remote_base_path']
    except IOError:
        print('No secret file found')
        host = input('Enter host: ').strip()
        username = input('Enter username: ').strip()
        password = input('Enter password: ').strip()

    if not quiet:
        print('Initiating SFTP connection with {}...'.format(host))

    # Login over sftp, calculate and apply diff
    with pysftp.Connection(host, username=username, password=password) as sftp:
        if not quiet:
            print('Downloading manifest')
        remote_manifest_data = load_remote_manifest(sftp, remote_base_path)
            
        if not quiet:
            print('Calculating diff')
        diff = current_app.manifest.calc_manifest_diff(remote_manifest_data)

        if diff.write_files or diff.del_files:
            apply_diff_remotely(sftp, remote_base_path, diff)
        else:
            print('Nothing to do: already synced!')
    

def load_remote_manifest(
        connection: pysftp.Connection,
        remote_base_path: str,
) -> typing.Dict[str, typing.Any]:
    # TODO: HOW TO MAKE MANIFEST CREATABLE LOCALLY, OR FROM REMOTE DATA? THEN WE COULD RETURN A MANIFEST INSTANCE 
    remote_manifest_path = remote_base_path + '/instance/manifest.json'
    if not connection.exists(remote_manifest_path):
        raise ValueError('Couldn\'t find manifest.json in remote')
    # Read the remote manifest into memory
    manifest_raw = io.BytesIO()  #io.TextIOWrapper()
    connection.getfo(remote_manifest_path, manifest_raw)
    manifest_raw.seek(0)
    return json.load(manifest_raw)['posts']


def apply_diff_remotely(
        connection: pysftp.Connection,
        remote_base_path: str,
        diff: mn.SyncDiff,
        quiet: bool = False,
):
    if not quiet:
        print('Applying diff...')
    # Make sure the 'static' folder exists
    remote_static_path = remote_base_path + '/flaskr/static'
    if not connection.exists(remote_static_path):  # TODO: USE `ISDIR()` INSTEAD
        raise ValueError('Couldn\'t find "static" folder in remote')

    # Determine the set of slugs to write and create their directories
    posts_to_write = set([mfile.post_slug for mfile in diff.write_files])
    for slug in posts_to_write:
        post_path = remote_static_path + '/' + slug
        # Create post directory if it doesn't exist
        if not connection.exists(post_path):
            if not quiet:
                print('Creating directory {}'.format(post_path))
            connection.mkdir(post_path)

    # Get path to local 'static' folder
    local_static_path = pathlib.Path(current_app.static_folder)

    # Write files
    for manifest_file in diff.write_files:
        local_file_path = \
            local_static_path / manifest_file.post_slug / manifest_file.filename
        remote_file_path = \
            remote_static_path + '/' + manifest_file.post_slug + '/' + manifest_file.filename
        if not quiet:
            print('Writing {}...'.format(remote_file_path))
        # print('Copying from {} to {}'.format(local_file_path, remote_file_path))
        connection.put(local_file_path, remote_file_path)
    
    # Delete files
    for manifest_file in diff.del_files:
        remote_file_path = \
            remote_static_path + '/' + manifest_file.post_slug + '/' + manifest_file.filename
        if not quiet:
            print('Deleting {}'.format(remote_file_path))
        connection.remove(remote_file_path)

    # Determine posts that have been removed, and delete their directories 
    # if now empty
    slugs_with_removal = set([mfile.post_slug for mfile in diff.del_files])
    for slug in slugs_with_removal:
        post_path = remote_static_path + '/' + slug
        if not connection.listdir(post_path):
            if not quiet:
                print('Deleting directory {}'.format(post_path))
            connection.rmdir(post_path)

    # Build remote paths
    remote_instance_path = remote_base_path + '/instance'
    remote_manifest_path = remote_instance_path + '/manifest.json'
    remote_database_path = remote_instance_path + '/posts.db'
    remote_search_index_path = remote_instance_path + '/index.json'

    # Upload the local manifest (which the remote manifest now matches)
    if not quiet:
        print('Uploading local manifest')
    connection.put(current_app.config['MANIFEST_PATH'], remote_manifest_path)

    # Upload local database
    if not quiet:
        print('Uploading local database')
    connection.put(current_app.config['DATABASE_PATH'], remote_database_path)

    # Upload local search index
    if not quiet:
        print('Uploading local search index')
    connection.put(current_app.config['SEARCH_INDEX_PATH'], remote_search_index_path)

    if not quiet:
        print('Done')