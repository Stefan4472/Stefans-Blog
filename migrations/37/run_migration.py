import pathlib
import sys
from sitemanager.manager_service import ManagerService
from sitemanager.postconfig import PostConfig, read_config_file


if __name__ == '__main__':
    """
    Run migration for Issue #37.
    
    This program will re-upload the Markdown files of the selected posts.
    
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
        config = read_config_file(post_dir / 'post-meta.json', use_imagecropper=False)
        with open(post_dir / 'post.md', encoding='utf-8', errors='strict') as f:
            markdown = f.read()
        print(f'Uploading Markdown for {config.slug}')
        service.upload_markdown(config.slug, markdown)
