import re
import randomcolor
from flaskr.database import db
import flaskr.models as models


KEY_TITLE = 'title'
KEY_BYLINE = 'byline'
KEY_SLUG = 'slug'
KEY_DATE = 'date'
KEY_TAGS = 'tags'
KEY_IMAGE = 'image'
KEY_BANNER = 'banner'
KEY_THUMBNAIL = 'thumbnail'
KEY_HASH = 'hash'
KEY_IMAGES = 'images'
KEY_FEATURED = 'is_featured'
KEY_PUBLISHED = 'is_published'

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


def generate_slug(
        string: str,
) -> str:
    """Generates a slug from the given string.

    Slugs are used to create readable urls.
    """
    string = string.replace(' ', '-').lower()
    # Remove any non letters, numbers, and non-dashes
    return re.sub(r'[^a-zA-Z0-9\-\+]+', '', string)


def generate_random_color() -> str:
    """Generates a random color and returns the hex string representing
    that color in RGB."""
    return randomcolor.RandomColor().generate(luminosity='light', count=1)[0]
