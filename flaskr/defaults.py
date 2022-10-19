import os
from typing import Dict
from flaskr.site_config import ConfigKeys


# Paths relative from the instance folder
DATABASE_REL_PATH = 'posts.sqlite'
# LOG_REL_PATH = 'log.txt'  TODO
TRAFFIC_LOG_REL_PATH = 'traffic.txt'  # TODO: should this be .csv?
SEARCH_INDEX_REL_PATH = 'index.json'

# Paths relative from the static folder (TODO)
# SITE_BANNER_REL_PATH = 'site_banner.jpg'
# Note: I'm actually not convinced we need these defaults.
# POST_BANNER_REL_PATH = 'default_banner.jpg'
# POST_THUMBNAIL_REL_PATH = 'default_thumbnail.jpg'
# POST_FEATURED_REL_PATH = 'default_featured.jpg'


def make_defaults(instance_path: str) -> Dict:
    return {
        ConfigKeys.SQLALCHEMY_DATABASE_URI: 'sqlite:///' + os.path.join(instance_path, DATABASE_REL_PATH),
        ConfigKeys.SQLALCHEMY_TRACK_MODIFICATIONS: False,
        ConfigKeys.TRAFFIC_LOG_PATH: os.path.join(instance_path, TRAFFIC_LOG_REL_PATH),
        ConfigKeys.SEARCH_INDEX_PATH: os.path.join(instance_path, SEARCH_INDEX_REL_PATH),
    }
