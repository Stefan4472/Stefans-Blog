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
KEY_PUBLISH = 'publish'
KEY_FEATURE = 'feature'
KEY_TITLE_COLOR = 'title_color'


# Expected data format for JSON
DATE_FORMAT = "%m/%d/%y"

# Regex used to match a HEX color for the `title_color` field
COLOR_REGEX = '^#[0-9a-fA-F]{6}$'

# Prescribed featured-image size (width, height)
FEATURED_IMG_SIZE = (1000, 540)
# Prescribed banner size
BANNER_SIZE = (1000, 175)
# Size of image thumbnails
THUMBNAIL_SIZE = (400, 400)
# The size that images in posts cannot exceed.
# Images that exceed this size will be thumbnail-ed to it.
MAX_IMG_SIZE = (1200, 800)
