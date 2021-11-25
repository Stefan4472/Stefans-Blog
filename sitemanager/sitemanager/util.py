import re
import pathlib
import hashlib


KEY_TITLE = 'title'
KEY_BYLINE = 'byline'
KEY_SLUG = 'slug'
KEY_DATE = 'date'
KEY_TAGS = 'tags'
KEY_IMAGE = 'image'
KEY_BANNER = 'banner'
KEY_THUMBNAIL = 'thumbnail'
KEY_PUBLISH = 'publish'
KEY_FEATURE = 'feature'

# Expected data format for JSON
DATE_FORMAT = "%m/%d/%y"

# Prescribed featured-image size
FEATURED_IMG_SIZE = (1000, 540)
# Prescribed banner size
BANNER_SIZE = (1000, 175) # (1928, 768)
# Size of image thumbnails
THUMBNAIL_SIZE = (400, 400)
# The size that images in posts are resized to, by default
DEFAULT_IMG_SIZE = (640, 480)


def generate_slug(string: str) -> str:
    """
    Generates a slug from the given string.

    Slugs are used to create readable urls.
    """
    string = string.replace(' ', '-').lower()
    # Remove any non letters, numbers, and non-dashes
    return re.sub(r'[^a-zA-Z0-9\-\+]+', '', string)


def get_static_url(rel_path_from_static: str) -> str:
    # TODO: FIND A WAY TO REFACTOR THIS OUT
    return '{{{{ url_for(\'static\', filename=\'{}\') }}}}'.format(
        rel_path_from_static
    )


def calc_hash(filepath: pathlib.Path) -> str:
    # Calculate hash of a file
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()
