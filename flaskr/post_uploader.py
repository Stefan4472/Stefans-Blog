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
    """SFTP instructions for PythonAnywhere: https://help.pythonanywhere.com/pages/SSHAccess"""
    # Read the secret file to get host information
    try:
        with open(current_app.config['SECRET_PATH']) as secret_file:
            secret_data = json.load(secret_file)
            host = secret_data['host']
            username = secret_data['username']
            password = secret_data['password']
            remote_base_path = secret_data['remote_base_path']
    except IOError:
        print ('No secret file found')
        host = input('Enter host: ').strip()
        username = input('Enter username: ').strip()
        password = input('Enter password: ').strip()

    if not quiet:
        print ('Initiating SFTP connection with {}...'.format(host))

    # Push files to PythonAnywhere, via SFTP
    # From cmd, the following correctly copies the 'inventory-systems' folder to PythonAnywhere:
    # 'put -r flaskr/static/inventory-systems Stefans-Blog/flaskr/static/inventory-systems'
    
    
    with pysftp.Connection(host, username=username, password=password) as sftp:
        remote_manifest_data = load_remote_manifest(sftp, remote_base_path)
        current_app.manifest.calc_manifest_diff(remote_manifest_data)
    #     # Create post directory on host and copy post files
    #     with sftp.cd(r'/home/skussmaul/Stefans-Blog/flaskr/static'):
    #         # Create post directory on host
    #         try:
    #             sftp.mkdir(slug)
    #         except IOError:
    #             print ('Warning: The directory already exists')
    #         # Enter post directory
    #         with sftp.cd(slug):
    #             # Copy all files in 'post_static_path' to host.
    #             # This is a workaround because the 'put_d' (put directory) command is not working.
    #             for file_to_copy in os.listdir(post_static_path):
    #                 if not quiet:
    #                     print ('Uploading {}...'.format(file_to_copy))
    #                 sftp.put(os.path.join(post_static_path, file_to_copy))
    #     # Copy instance files
    #     with sftp.cd(r'/home/skussmaul/Stefans-Blog/instance'):
    #         sftp.put(current_app.config['DATABASE_PATH'])
    #         sftp.put(current_app.config['SEARCH_INDEX_PATH'])

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
