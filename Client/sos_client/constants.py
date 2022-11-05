"""API constants. Copied from flaskr/api/constants.py."""
# Expected data format for JSON
DATE_FORMAT = "%m/%d/%y"

# Regex used to match a HEX color for the `title_color` field
COLOR_REGEX = r'^#[0-9a-fA-F]{6}$'
# Regex used to validate a post slug
SLUG_REGEX = r'^[0-9a-zA-Z\-]+$'

# Prescribed featured-image size (width, height)
FEATURED_IMG_SIZE = (1000, 540)
# Prescribed banner size
BANNER_SIZE = (1000, 175)
# Size of image thumbnails
THUMBNAIL_SIZE = (400, 400)