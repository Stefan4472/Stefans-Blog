import re
import pathlib
import shutil
import typing
import datetime
from PIL import Image
import dataclasses as dc
import json
import markdown2 as md
import randomcolor
import flaskr.database as db
from flaskr.image_cropper.image_cropper import ImageCropper
# from flaskr.manifest import Manifest
import tkinter as tk
from tkinter.filedialog import askopenfilename


# Keys used in post-meta.json
KEY_TITLE = 'title'
KEY_BYLINE = 'byline'
KEY_SLUG = 'slug'
KEY_DATE = 'date'
KEY_TAGS = 'tags'
KEY_IMAGE = 'image'
KEY_BANNER = 'banner'
KEY_THUMBNAIL = 'thumbnail'

# RandomColor object used to generate Tag colors
COLOR_GENERATOR = randomcolor.RandomColor()

# Prescribed featured-image size
FEATURED_IMG_SIZE = (1000, 540)
# Prescribed banner size
BANNER_SIZE = (1000, 175) # (1928, 768)
# Size of image thumbnails
THUMBNAIL_SIZE = (400, 400)
# The size that images in posts are resized to, by default
DEFAULT_IMG_SIZE = (640, 480)


@dc.dataclass
class PostImage:
    image: Image.Image
    in_memory_only: bool
    path: typing.Optional[pathlib.Path] = None


@dc.dataclass
class PostImages:
    featured: PostImage
    thumbnail: PostImage
    banner: PostImage


@dc.dataclass
class PostData:
    title: str
    byline: str
    slug: str
    post_date: datetime.datetime
    featured_img: PostImage
    thumbnail_img: PostImage
    banner_img: PostImage
    tags: typing.List[str] = dc.field(default_factory=list)
    html: str = ''
    images: typing.List[PostImage] = dc.field(default_factory=list)


# Generates a slug given a string.
# Slugs are used to create readable urls
def generate_slug(string):
    string = string.replace(' ', '-').lower()
    # Remove any non letters, numbers, and non-dashes
    return re.sub(r'[^a-zA-Z0-9\-\+]+', '', string)


# TODO: FLASK PROVIDES A METHOD FOR THIS
def get_static_url(filepath):
    return '{{{{ url_for(\'static\', filename=\'{}\') }}}}'.format(filepath)


def generate_random_color():
    return COLOR_GENERATOR.generate(luminosity='light', count=1)[0]


def resolve_directory_path(
        starting_dir: pathlib.Path,
        path: str,
) -> pathlib.Path:
    # Check the absolute path
    abs_path = pathlib.Path(path)
    if abs_path.is_dir():
        return abs_path
    # If that didn't work, check the relative path
    rel_path = pathlib.Path(starting_dir) / path
    if rel_path.is_dir():
        return rel_path
    # If that didn't work, raise error
    raise ValueError('Couldnt\'t find directory at absolute or relative path')


def resolve_file_path(
        starting_dir: pathlib.Path,
        path: str,
) -> pathlib.Path:
    # Check the absolute path
    abs_path = pathlib.Path(path)
    if abs_path.is_file():
        return abs_path
    # If that didn't work, check the relative path
    rel_path = pathlib.Path(starting_dir) / path
    if rel_path.is_file():
        return rel_path
    # If that didn't work, raise error
    raise ValueError('Couldnt\'t find file at absolute or relative path')
      

def read_meta_file(
        filepath: pathlib.Path,
) -> typing.Dict[str, typing.Any]:
    """Read and return the JSON from the provided meta-data file."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='strict') as f:
            return json.load(f)
    except IOError:
        raise ValueError(
            'Could not read the meta-data file ("{}")'.format(filepath))
    except json.JSONDecodeError as e:  # TODO: TEST THAT THIS WORKS AS EXPECTED
        print(e)


def process_post_meta(
        post_dir: pathlib.Path,
        post_meta: typing.Dict[str, typing.Any],
) -> PostData:
    title = get_post_title(post_meta)
    byline = get_post_byline(post_meta)
    slug = get_post_slug(post_meta, title)
    post_date = get_post_date(post_meta)
    post_images = get_post_images(post_dir, post_meta)
    tags = post_meta['tags'] if 'tags' in post_meta else []

    return PostData(
        title=title,
        byline=byline,
        slug=slug,
        post_date=post_date,
        featured_img = post_images.featured,
        thumbnail_img = post_images.thumbnail,
        banner_img = post_images.banner,
        tags=tags,
    )


def get_post_title(
        post_meta: typing.Dict[str, typing.Any],
) -> str:
    if KEY_TITLE in post_meta:
        return post_meta[KEY_TITLE]
    else:
        raise ValueError(
            'post-meta.json must contain a "{}" field'.format(KEY_TITLE))


def get_post_byline(
        post_meta: typing.Dict[str, typing.Any],
) -> str:
    if KEY_BYLINE in post_meta:
        byline = post_meta[KEY_BYLINE]
        # Make sure byline is not more than 200 characters
        if len(byline) > 200:
            byline = byline[:200]
        return byline
    else:
        # Just take the first 200 characters of Markdown
        # TODO: INSTEAD, GRAB THE CONTENTS OF THE FIRST '<p>' TAG?
        # byline = post_markdown[:200]
        raise ValueError(
            'post-meta.json must contain a "{}" field'.format(KEY_BYLINE))


def get_post_slug(
        post_meta: typing.Dict[str, typing.Any],
        post_title: str,
) -> str:
    # Get slug
    if KEY_SLUG in post_meta:
        return post_meta[KEY_SLUG]
    else:
        # Generate slug from title if needed
        return generate_slug(post_title)


def get_post_date(
        post_meta: typing.Dict[str, typing.Any],
) -> datetime.datetime:
    if KEY_DATE in post_meta:
        # Parse the date in the format "MM/DD/YY"
        return datetime.datetime.strptime(post_meta[KEY_DATE], "%m/%d/%y")# .date()
    else:  
        # Default to today's date
        return date.today()


def get_post_images(
        post_dir: pathlib.Path,
        post_meta: typing.Dict[str, typing.Any],
) -> PostImages:
    """Return featured image, thumbnail, banner image."""
    # If image has been defined, get the other images from json. 
    # Otherwise, run ImageCropper.
    if KEY_IMAGE in post_meta:
        return get_post_images_from_json(post_dir, post_meta)
    else:
        return get_post_images_from_image_cropper(post_dir)


def get_post_images_from_json(
        post_dir: pathlib.Path,
        post_meta: typing.Dict[str, typing.Any],
) -> PostImages:
    # Get featured image
    post_img_path = post_dir / post_meta[KEY_IMAGE]
    post_img = Image.open(post_img_path)
    if post_img.width != FEATURED_IMG_SIZE[0] or \
            post_img.height != FEATURED_IMG_SIZE[1]:
        raise ValueError(
            'Featured image must be {}w x {}h px'.format(
                FEATURED_IMG_SIZE[0], FEATURED_IMG_SIZE[1])
        )

    # Get banner image
    if KEY_BANNER in post_meta:
        banner_path = post_dir / post_meta[KEY_BANNER]
        banner_img = Image.open(banner_path)
        if banner_img.width != BANNER_SIZE[0] or banner_img.height != BANNER_SIZE[1]:
            raise ValueError(
                'Banner image must be {}w x {}h px'.format(
                    BANNER_SIZE[0], BANNER_SIZE[1])
            )
    else:
        raise ValueError(
            'post-meta.json must contain a "{}" field'.format(KEY_BANNER)
        )

    # Get thumbnail image
    if KEY_THUMBNAIL in post_meta:
        thumbnail_path = post_dir / post_meta[KEY_THUMBNAIL]
        thumbnail_img = Image.open(thumbnail_path)
        if thumbnail_img.width != THUMBNAIL_SIZE[0] or \
                thumbnail_img.height != THUMBNAIL_SIZE[1]:
            raise ValueError(
                'Banner image must be {}w x {}h px'.format(
                    THUMBNAIL_SIZE[0], THUMBNAIL_SIZE[1])
            )
    else:
        raise ValueError(
            'post-meta.json must contain a "{}" field'.format(KEY_THUMBNAIL)
        )

    return PostImages(
        featured=PostImage(post_img, False, path=post_img_path),
        thumbnail=PostImage(thumbnail_img, False, path=thumbnail_path),
        banner=PostImage(banner_img, False, path=banner_path),
    )


def get_post_images_from_image_cropper(
        post_dir: pathlib.Path,
) -> PostImages:
    root = tk.Tk()
    # Ask user to select an image for use
    img_path = askopenfilename(
        initialdir=post_dir,
        title = 'Select image',
        filetypes = (
            ('jpg files','*.jpg'), 
            ('jpeg files', '*.jpeg'), 
            ('png files', '*.png'), 
            ('gif files', '*.gif'),
        ),
    )
    # Exit if user did not select an image
    if not img_path:
        raise ValueError('No image selected')

    img_path = pathlib.Path(img_path)

    # Create featured image
    app = ImageCropper(img_path, FEATURED_IMG_SIZE[0], FEATURED_IMG_SIZE[1])
    app.mainloop()
    if app.finished_successfully:
        featured_img = app.cropped_image
    else:
        raise ValueError('Operation cancelled')
    
    # Create thumbnail
    app = ImageCropper(str(img_path), THUMBNAIL_SIZE[0], THUMBNAIL_SIZE[1])
    app.mainloop()
    if app.finished_successfully:
        thumbnail_img = app.cropped_image
    else:
        raise ValueError('Operation cancelled')

    # Create banner
    app = ImageCropper(img_path, BANNER_SIZE[0], BANNER_SIZE[1])
    app.mainloop()
    if app.finished_successfully:
        banner_img = app.cropped_image
    else:
        raise ValueError('Operation cancelled')

    # Create the paths for the newly-cropped images
    featured_path = post_dir / 'featured.jpg'
    thumbnail_path = post_dir / 'thumb.jpg'
    banner_path = post_dir / 'banner.jpg'

    # Save the images
    featured_img.save(featured_path)
    thumbnail_img.save(thumbnail_path)
    banner_img.save(banner_path)

    return PostImages(
        featured=PostImage(featured_img, False, path=featured_path),
        thumbnail=PostImage(thumbnail_img, False, path=thumbnail_path),
        banner=PostImage(banner_img, False, path=banner_path),
    )


def render_markdown_file(
        filepath: pathlib.Path,
        post_slug: str,
) -> typing.Tuple[str, typing.List[str]]:
    """Read the provided Markdown file and render to HTML. 
    Images will be redered as Bootstrap figures.
    
    Returns the HTML as a string, and a list of all image sources
    found in the document.
    
    TODO: EXPLAIN HOW TO ADD A CAPTION
    TODO: THIS WHOLE FUNCTION SHOULD BE CLEANED UP, AND SHOULDN'T DEAL WITH 'IMG_SAVE_DIR'
    -> create "Markdown Processer" class
    """
    # Regex used to match custom "[figure]" lines.
    # Match 1: image path
    # Match 2: optional image caption
    figure_regex = re.compile(r'\[figure: ([^,\]]+)(?:, ([^\]]+))?]')
    html_snippets = []
    images = []
    last_match_index = -1

    try:
        with open(filepath, 'r', encoding='utf-8', errors='strict') as f:
            post_markdown = f.read()
    except IOError:
        raise ValueError(
            'Could not read the post file ("{}")'.format(filepath))
    
    # Iterate through '[figure: ]' instances, which must be handled specially.
    # Everything else can be rendered using the 'markdown' library.
    for figure_match in re.finditer(figure_regex, post_markdown):
        start = figure_match.start()
        end = figure_match.end()
        
        # Render the Markdown between the end of the last figure match and the start of
        # this figure match (if it is non-whitespace)
        if (start != last_match_index + 1) and post_markdown[last_match_index + 1 : start].strip():
            rendered_html = md.markdown(post_markdown[last_match_index + 1 : start], extras=['fenced-code-blocks'])
            html_snippets.append(rendered_html)

        # Render the figure
        img_path = figure_match.group(1)
        img_caption = figure_match.group(2)

        # TODO: CLEAN UP
        img_url = get_static_url(post_slug + '/' + pathlib.Path(img_path).name) 

        # Render with caption
        # TODO: HANDLE alt, and make this string a constant (?)
        # TODO: ANY WAY TO MAKE THE BACKGROUND COLOR OF THE CAPTION GRAY, AND LIMIT IT TO THE WIDTH OF THE TEXT?
        if img_caption:
            rendered_html = \
'''
<figure class="figure text-center">
    <img src="{}" class="figure-img img-fluid" alt="">
    <figcaption class="figure-caption">{}</figcaption>
</figure>

'''.format(img_url, img_caption)
        # Render without caption
        else:
            rendered_html = \
'''
<figure class="figure text-center">
    <img src="{}" class="figure-img img-fluid" alt="">
</figure>

'''.format(img_url)
        
        images.append(img_path)
        html_snippets.append(rendered_html)
        last_match_index = end

    # Render the Markdown from the last figure match to the end of the file
    if last_match_index != len(post_markdown):
        rendered_html = md.markdown(post_markdown[last_match_index + 1 :], extras=['fenced-code-blocks'])
        html_snippets.append(rendered_html)
        #print (rendered_html)
    
    return ''.join(html_snippets), images


def process_post_images(
        post_dir: pathlib.Path,
        post_static_path: pathlib.Path,
        img_sources: typing.List[str],
) -> typing.List[PostImage]:
    post_images: typing.List[PostImage] = []
    # Copy image files to the article's directory
    for img_src in img_sources:
        # Ignore image links
        if img_src.startswith('http') or img_src.startswith('www'):
            continue 
        
        # Get absolute path to image
        try:
            img_path = resolve_file_path(post_dir, img_src)
        except ValueError as e:
            print(e)
            continue

        img = Image.open(img_path)

        # Resize non-gif images
        if img_path.suffix != '.gif':
            img.thumbnail(DEFAULT_IMG_SIZE, Image.ANTIALIAS)
            #img = img.convert('RGB')
        
        post_images.append(PostImage(img, False, path=img_path))
        
    return post_images
    

def add_post_to_database(
        post_static_url: str,
        db_path: pathlib.Path,
        post_data: PostData,
):
    # Get connection to the post database
    database = db.Database(str(db_path))
    # Add post to the database.
    # This will fail if there is a problem with the post data
    # TODO: ACTUALLY, THE URLS SHOULD ALL BE STANDARDIZED AND DON'T NEED TO BE STORED IN THE DATABASE
    database.add_post(
        post_data.title,
        post_data.byline,
        post_data.slug,
        post_data.post_date.date(),
        post_static_url + '/' + 'featured.jpg',
        post_static_url + '/' + 'banner.jpg',
        post_static_url + '/' + 'thumbnail.jpg',
    )

    # Add tags to the database
    for tag in post_data.tags:
        tag_slug = generate_slug(tag)
        # Add tag to the database if it doesn't already exist
        if not database.has_tag(tag_slug):
            database.add_tag(
                tag,
                tag_slug, 
                generate_random_color(),
            )
        # Add post->tag mapping to database
        database.add_tag_to_post(tag_slug, post_data.slug)
    # TODO: ANY WAY TO *NOT* HAVE TO COMMIT BY DEFAULT?
    database.commit()


def copy_to_static(
        static_path: pathlib.Path,
        file_path: pathlib.Path,
):  
    # TODO: IMPROVE
    # Make sure the file exists
    if not file_path.is_file():
        raise ValueError('The file "{}" is not a real file'.format(file_path))  # TODO: RAISE EXCEPTION

    # Build destination path
    dest_path = static_path / file_path.name
    # print('Copying {} to {}'.format(file_path, dest_path))
    # Copy the image to the folder
    shutil.copyfile(file_path, dest_path)
