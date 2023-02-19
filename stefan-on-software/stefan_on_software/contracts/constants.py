# Expected data format for JSON
DATE_FORMAT = "%m/%d/%y"

# Regex used to match a HEX color for the `title_color` field
COLOR_REGEX = r"^#[0-9a-fA-F]{6}$"
# Regex used to validate a post slug
SLUG_REGEX = r"^[0-9a-zA-Z\-\+]+$"

# Prescribed featured-image size (width, height)
FEATURED_IMAGE_WIDTH = 1000
FEATURED_IMAGE_HEIGHT = 540
# Prescribed banner size
BANNER_WIDTH = 1000
BANNER_HEIGHT = 175
# Size of image thumbnails
THUMBNAIL_WIDTH = 400
THUMBNAIL_HEIGHT = 400
# The size that images in posts cannot exceed.
# Images that exceed this size will be thumbnail-ed to it.
MAX_IMG_WIDTH = 1200
MAX_IMG_HEIGHT = 800
