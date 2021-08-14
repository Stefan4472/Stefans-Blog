import re
import pathlib
import hashlib


KEY_TITLE = 'title'
KEY_BYLINE = 'byline'
KEY_SLUG = 'slug'
KEY_DATE = 'date'
KEY_TAGS = 'tags'
KEY_FEATURED = 'image'
KEY_BANNER = 'banner'
KEY_THUMBNAIL = 'thumbnail'

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


# def get_post_images(
#         post_dir: pathlib.Path,
#         post_meta: typing.Dict[str, typing.Any],
# ) -> PostImages:
#     """Return featured image, thumbnail, banner image."""
#     # If image has been defined, get the other images from json.
#     if KEY_IMAGE in post_meta:
#         return get_post_images_from_json(post_dir, post_meta)
#     # Otherwise, run ImageCropper.
#     else:
#         return get_post_images_from_image_cropper(post_dir)
#
#
# def get_post_images_from_json(
#         post_dir: pathlib.Path,
#         post_meta: typing.Dict[str, typing.Any],
# ) -> PostImages:
#     # TODO: ALLOW ABSOLUTE *OR* RELATIVE PATHS
#     # Get featured image
#     if KEY_IMAGE in post_meta:
#         # Construct relative path
#         post_img_path = post_dir / post_meta[KEY_IMAGE]
#         # Make sure the provided image is a .jpg
#         if post_img_path.suffix != '.jpg':
#             raise ValueError('"{}" must be a .jpg file'.format(KEY_IMAGE))
#         # Read into memory and check that the dimensions are exactly correct
#         post_img = Image.open(post_img_path)
#         if (post_img.width, post_img.height) != FEATURED_IMG_SIZE:
#             raise ValueError(
#                 'Featured image must be {}w x {}h px'.format(
#                     FEATURED_IMG_SIZE[0], FEATURED_IMG_SIZE[1]
#                 )
#             )
#     else:
#         raise ValueError(
#             'post-meta.json must contain a "{}" field'.format(KEY_IMAGE)
#         )
#
#     # Get banner image
#     if KEY_BANNER in post_meta:
#         banner_path = post_dir / post_meta[KEY_BANNER]
#         if banner_path.suffix != '.jpg':
#             raise ValueError('"{}" must be a .jpg file'.format(KEY_BANNER))
#         banner_img = Image.open(banner_path)
#         if (banner_img.width, banner_img.height) != BANNER_SIZE:
#             raise ValueError(
#                 'Banner image must be {}w x {}h px'.format(
#                     BANNER_SIZE[0], BANNER_SIZE[1])
#             )
#     else:
#         raise ValueError(
#             'post-meta.json must contain a "{}" field'.format(KEY_BANNER)
#         )
#
#     # Get thumbnail image
#     if KEY_THUMBNAIL in post_meta:
#         thumbnail_path = post_dir / post_meta[KEY_THUMBNAIL]
#         if thumbnail_path.suffix != '.jpg':
#             raise ValueError('"{}" must be a .jpg file'.format(KEY_THUMBNAIL))
#         thumbnail_img = Image.open(thumbnail_path)
#         if (thumbnail_img.width, thumbnail_img.height) != THUMBNAIL_SIZE:
#             raise ValueError(
#                 'Banner image must be {}w x {}h px'.format(
#                     THUMBNAIL_SIZE[0], THUMBNAIL_SIZE[1]
#                 )
#             )
#     else:
#         raise ValueError(
#             'post-meta.json must contain a "{}" field'.format(KEY_THUMBNAIL)
#         )
#
#     return PostImages(
#         featured=PostImage(post_img, False, path=post_img_path),
#         thumbnail=PostImage(thumbnail_img, False, path=thumbnail_path),
#         banner=PostImage(banner_img, False, path=banner_path),
#     )
#
#
# def get_post_images_from_image_cropper(
#         post_dir: pathlib.Path,
# ) -> PostImages:
#     root = tk.Tk()
#     # Ask user to select an image for use
#     img_path = askopenfilename(
#         initialdir=post_dir,
#         title='Select featured image',
#         filetypes=(
#             ('jpg files', '*.jpg'),
#             ('jpeg files', '*.jpeg'),
#             ('png files', '*.png'),
#             ('gif files', '*.gif'),
#         ),
#     )
#     # Exit if user did not select an image
#     if not img_path:
#         raise ValueError('No image selected')
#
#     img_path = pathlib.Path(img_path)
#
#     # Create featured image
#     app = ImageCropper(img_path, FEATURED_IMG_SIZE[0], FEATURED_IMG_SIZE[1])
#     app.mainloop()
#     if app.finished_successfully:
#         featured_img = app.cropped_image
#     else:
#         raise ValueError('Operation cancelled')
#
#     # Create thumbnail
#     app = ImageCropper(str(img_path), THUMBNAIL_SIZE[0], THUMBNAIL_SIZE[1])
#     app.mainloop()
#     if app.finished_successfully:
#         thumbnail_img = app.cropped_image
#     else:
#         raise ValueError('Operation cancelled')
#
#     # Create banner
#     app = ImageCropper(img_path, BANNER_SIZE[0], BANNER_SIZE[1])
#     app.mainloop()
#     if app.finished_successfully:
#         banner_img = app.cropped_image
#     else:
#         raise ValueError('Operation cancelled')
#
#     # Create the paths for the newly-cropped images
#     featured_path = post_dir / 'featured.jpg'
#     thumbnail_path = post_dir / 'thumb.jpg'
#     banner_path = post_dir / 'banner.jpg'
#
#     # Save the images
#     featured_img.save(featured_path)
#     thumbnail_img.save(thumbnail_path)
#     banner_img.save(banner_path)
#
#     return PostImages(
#         featured=PostImage(featured_img, False, path=featured_path),
#         thumbnail=PostImage(thumbnail_img, False, path=thumbnail_path),
#         banner=PostImage(banner_img, False, path=banner_path),
#     )
