import sys
import pathlib
from sos_client.manager import upload_post_from_dir
from sos_client.manager_service import ManagerService
from sos_client.postconfig import read_config_file


if __name__ == '__main__':
    """
    Run migration for Issue #45.

    This program will re-upload all posts to the site, once Issue #45 has
    been deployed. It should be run on the machine that stores post data.
    The host will need to reset its database before this is executed! 
    
    Because of the database reset, the user will need to reset the site's
    Featured posts. 

    FILEPATH: path to a text file that contains all the post paths to migrate
    HOST: host url
    SECRET_KEY: secret used to authenticate API calls
    """
    if len(sys.argv) != 4:
        print('Usage: python run_migration.py [FILEPATH] [HOST] [SECRET_KEY]')
        sys.exit(1)

    filepath = sys.argv[1]
    host = sys.argv[2]
    key = sys.argv[3]

    service = ManagerService(host, key)
    with open(filepath) as f:
        paths = f.readlines()

    # For each path, read config, then upload markdown
    for path_str in paths:
        post_dir = pathlib.Path(path_str.strip())
        upload_post_from_dir(post_dir, host, key, False, True, False, True)
