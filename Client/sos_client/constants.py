"""API constants. Copied from flaskr/api/constants.py."""
# Expected data format for JSON
DATE_FORMAT = "%m/%d/%y"

# Regex used to match a HEX color for the `title_color` field
COLOR_REGEX = r'^#[0-9a-fA-F]{6}$'
# Regex used to validate a post slug
SLUG_REGEX = r'^[0-9a-zA-Z\-]+$'

# Prescribed featured-image size (width, height)
FEATURED_IMAGE_WIDTH = 1000
FEATURED_IMAGE_HEIGHT = 540
FEATURED_IMAGE_SIZE = (FEATURED_IMAGE_WIDTH, FEATURED_IMAGE_HEIGHT)
# Prescribed banner size
BANNER_WIDTH = 1000
BANNER_HEIGHT = 175
BANNER_SIZE = (BANNER_WIDTH, BANNER_HEIGHT)
# Size of image thumbnails
THUMBNAIL_WIDTH = 400
THUMBNAIL_HEIGHT = 400
THUMBNAIL_SIZE = (THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT)