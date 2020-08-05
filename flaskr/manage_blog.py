# TODO: PUT THIS IN ITS OWN FOLDER? USE CLICK TO MAKE IT INTO A FLASK COMMAND?
import sys  
import re
import os
import pathlib
import shutil
import click
import pysftp
import typing
from datetime import date, datetime
from flask import current_app, url_for
from flask.cli import with_appcontext
from PIL import Image
import json
import markdown2 as md
import randomcolor
from flaskr.database import Database
import flaskr.search_engine.index as index  # TODO: BETTER IMPORTS
from flaskr.image_cropper.image_cropper import ImageCropper
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

# Generates a slug given a string.
# Slugs are used to create readable urls
def generate_slug(string):
    string = string.replace(' ', '-').lower()
    # Remove any non letters, numbers, and non-dashes
    return re.sub(r'[^a-zA-Z0-9\-\+]+', '', string)

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
        
# Takes the path to a Markdown file, read it, and renders it to HTML.
# Returns (rendered HTML as a string, list of image sources found in <img> tags).
# This function will render images as Bootstrap figures. 
# TODO: EXPLAIN HOW TO ADD A CAPTION
# TODO: THIS WHOLE FUNCTION SHOULD BE CLEANED UP, AND SHOULDN'T DEAL WITH 'IMG_SAVE_DIR'
def render_md_file(file_path, img_save_dir):
    # Regex used to match custom "[figure]" lines.
    # Match 1: image path
    # Match 2: optional image caption
    figure_regex = re.compile(r'\[figure: ([^,\]]+)(?:, ([^\]]+))?]')
    html_snippets = []
    images = []
    md_text = ''
    last_match_index = -1

    # print ('Reading file...')
    with open(file_path, 'r', encoding='utf-8', errors='strict') as md_file:
        md_text = md_file.read()
    
    # Iterate through '[figure: ]' instances, which must be handled specially.
    # Everything else can be rendered using the 'markdown' library.
    for figure_match in re.finditer(figure_regex, md_text):
        start = figure_match.start()
        end = figure_match.end()
        
        # Render the Markdown between the end of the last figure match and the start of
        # this figure match (if it is non-whitespace)
        if (start != last_match_index + 1) and md_text[last_match_index + 1 : start].strip():
            rendered_html = md.markdown(md_text[last_match_index + 1 : start], extras=['fenced-code-blocks'])
            html_snippets.append(rendered_html)

        # Render the figure
        img_path = figure_match.group(1)
        img_caption = figure_match.group(2)
        # print (img_path, img_caption)
        img_url = get_static_url(img_save_dir + '/' + os.path.basename(img_path))  # TODO: CLEAN UP

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
    if last_match_index != len(md_text):
        rendered_html = md.markdown(md_text[last_match_index + 1 :], extras=['fenced-code-blocks'])
        html_snippets.append(rendered_html)
        #print (rendered_html)
    
    return ''.join(html_snippets), images


def copy_to_static(file_path, static_path):  # TODO: IMPROVE
    # Make sure the file exists
    if not (os.path.exists(file_path) and os.path.isfile(file_path)):
        print ('ERROR: The image path "{}" is not a real file'.format(file_path))  # TODO: RAISE EXCEPTION
        return

    # Build destination path for the image
    dest_path = os.path.join(static_path, os.path.basename(file_path))
    # print (dest_path)
    
    # Copy the image to the folder
    shutil.copyfile(file_path, dest_path)


def process_post_data(
        post_data: typing.Dict[str, typing.Any],
) -> typing.Tuple[str, str, str, datetime]:
    # Make sure title is defined
    if KEY_TITLE in post_data:
        title = post_data[KEY_TITLE]
    else:
        raise ValueError('post-meta.json must contain a "{}" field'.format(KEY_TITLE))

    # Get byline
    if KEY_BYLINE in post_data:
        byline = post_data[KEY_BYLINE]
        # Make sure byline is not more than 200 characters
        if len(byline) > 200:
            byline = byline[:200]
    else:
        # Just take the first 200 characters of Markdown
        # TODO: INSTEAD, GRAB THE CONTENTS OF THE FIRST '<p>' TAG?
        byline = post_markdown[:200]

    # Get slug
    if KEY_SLUG in post_data:
        slug = post_data[KEY_SLUG]
    else:
        # Generate slug from title if needed
        slug = generate_slug(title)

    # Get publish date
    if KEY_DATE in post_data:
        # Parse the date in the format "MM/DD/YY"
        post_date = datetime.strptime(post_data[KEY_DATE], "%m/%d/%y").date()
    else:  
        # Default to today's date
        post_date = date.today()
    return title, byline, slug, post_date


class PostImages:
    def __init__(
            self,        
            featured_img: Image.Image = None,
            featured_img_path: str = '',
            thumbnail_img: Image.Image = None,
            thumbnail_img_path: str = '',
            banner_img: Image.Image = None,
            banner_img_path: str = '',
            changed: bool = False,
    ):
        self.featured_img = featured_img
        self.featured_img_path = featured_img_path
        self.thumbnail_img = thumbnail_img
        self.thumbnail_img_path = thumbnail_img_path
        self.banner_img = banner_img
        self.banner_img_path = banner_img_path
        self.changed = changed


def get_post_images(
        post_dir: pathlib.Path,
        post_data: typing.Dict[str, typing.Any],
) -> PostImages:
    """Return featured image, thumbnail, banner image."""
    # If image has been defined, get the other images from json. 
    # Otherwise, run ImageCropper.
    if KEY_IMAGE in post_data:
        return get_post_images_from_json(post_dir, post_data)
    else:
        return get_post_images_from_image_cropper(post_dir)


def get_post_images_from_json(
        post_dir: pathlib.Path,
        post_data: typing.Dict[str, typing.Any],
) -> PostImages:
    # Get featured image
    post_img_path = post_dir / post_data[KEY_IMAGE]
    post_img = Image.open(post_img_path)
    if post_img.width != FEATURED_IMG_SIZE[0] or \
            post_img.height != FEATURED_IMG_SIZE[1]:
        raise ValueError(
            'Featured image must be {}w x {}h px'.format(
                FEATURED_IMG_SIZE[0], FEATURED_IMG_SIZE[1])
        )

    # Get banner image
    if KEY_BANNER in post_data:
        banner_path = post_dir / post_data[KEY_BANNER]
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
    if KEY_THUMBNAIL in post_data:
        thumbnail_path = post_dir / post_data[KEY_THUMBNAIL]
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
        featured_img=post_img,
        featured_img_path=post_img_path,
        thumbnail_img=thumbnail_img,
        thumbnail_img_path=thumbnail_path,
        banner_img=banner_img,
        banner_img_path=banner_path,
        changed=True,
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
        post_img = app.cropped_image
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
    post_img.save(featured_path)
    thumbnail_img.save(thumbnail_path)
    banner_img.save(banner_path)

    return PostImages(
        featured_img=post_img,
        featured_img_path=featured_path.name,
        thumbnail_img=thumbnail_img,
        thumbnail_img_path=thumbnail_path.name,
        banner_img=banner_img,
        banner_img_path=banner_path.name,
    )
    

@click.command('add_post')
@click.argument('post_dir')
@click.option('--quiet', is_flag=True, default=False, help='Whether to suppress print statements and confirmation prompts')
@with_appcontext
def add_post(
        post_dir: str, 
        quiet: bool, 
):
    try:
        post_dir = resolve_directory_path(sys.argv[0], post_dir)
    except ValueError as e:
        print(e)
        sys.exit(1)

    if not quiet:
        print('Adding post from directory "{}"'.format(post_dir))
    
    # Determine absolute path to the post file and the metadata file
    post_path = post_dir / 'post.md'
    meta_path = post_dir / 'post-meta.json'

    # Post's Markdown
    post_markdown = ''
    # Post's generated HTML
    post_html = ''
    # Post's metadata
    post_data: typing.Dict[str, typing.Any] = {}

    # Read the metadata file
    try:
        with open(meta_path, 'r', encoding='utf-8', errors='strict') as meta_file:
            post_data = json.load(meta_file)
    except IOError:
        print ('ERROR: Could not read the meta-data file ("{}")'.format(meta_path))
        sys.exit(1)

    # Read the Markdown file 
    try:
        with open(post_path, 'r', encoding='utf-8', errors='strict') as post_file:
            post_markdown = post_file.read()
    except IOError:
        print ('ERROR: Could not read the post file ("{}")'.format(post_path))
        sys.exit(1)

    title, byline, slug, post_date = process_post_data(post_data)
    
    post_images = get_post_images(post_dir, post_data)

    # Write image paths to the 'post-meta.json' file, overwriting
    # any paths that are currently there. This is done in case the
    # user has selected new images that weren't there before
    if post_images.changed:
        post_data['image'] = str(post_images.featured_img_path.name)
        post_data['thumbnail'] = str(post_images.thumbnail_img_path.name)
        post_data['banner'] = str(post_images.banner_img_path.name)
        
    # TODO: HOW TO UPDATE METADATA PROPERLY?
    # Write out the updated post metadata
    try:
        with open(meta_path, 'w') as meta_file:
            json.dump(post_data, meta_file, indent=4)
            print('Saved images and updated "post-meta.json" successfully')
    except IOError:
        print('Couldn\'t update the meta-data file ("{}")'.format(meta_path))
        sys.exit(1)

    # Build URLs for the image, banner, and thumbnail.
    # They will have prescribed filenames ('image', 'banner', 'thumbnail') 
    post_img_url = current_app.static_url_path + '/' + slug + '/featured_img.jpg'
    post_banner_url = current_app.static_url_path + '/' + slug + '/banner.jpg'
    post_thumbnail_url = current_app.static_url_path + '/' + slug + '/thumbnail.jpg'
    
    # Get connection to the post database
    database = Database(current_app.config['DATABASE_PATH'])

    # Add post to the database.
    # This will fail if there is a problem with the post data
    # TODO: ACTUALLY, THE URLS SHOULD ALL BE STANDARDIZED AND DON'T NEED TO BE STORED IN THE DATABASE
    database.add_post(
        title, 
        byline, 
        slug, 
        post_date, 
        post_img_url, 
        post_banner_url, 
        post_thumbnail_url,
    )

    # Add tags to the database
    if KEY_TAGS in post_data:
        for tag in post_data[KEY_TAGS]:
            # print ('Handling tag {}'.format(tag))
            tag_slug = generate_slug(tag)
            # Add tag to the database if not already there
            if not database.has_tag(tag_slug):
                tag_color = generate_random_color()
                database.add_tag(tag, tag_slug, tag_color)
            # Add post->tag mapping to database
            database.add_tag_to_post(tag_slug, slug)
    
    # Get path to where the post data will live on this filesystem ('...\static\[slug]')
    post_static_path = os.path.join(current_app.static_folder, slug)

    # Create the directory for the post data
    try:
        os.mkdir(post_static_path)
    except FileExistsError:
        # Ignore if quiet option set
        if quiet:
            pass
        # Ask user for confirmation before continuing
        else:
            confirm_use_dir = 'n'
            while confirm_use_dir != 'y':
                confirm_use_dir = input('The post directory "{}" already exists. Continue? (y/n)'.format(post_static_path)).strip().lower()
                if confirm_use_dir == 'n':
                    print('No changes made--aborted')
                    sys.exit(1)

    # Render the Markdown file to HTML  NOTE: THE FILE HAS ALREADY BEEN READ!
    article_html, article_imgs = render_md_file(post_path, slug)  # TODO: IS THIS HANDLING BLANK LINES CORRECTLY?
    
    # Save post images to 'static'
    post_images.featured_img.save(os.path.join(post_static_path, 'featured_img.jpg'))
    post_images.banner_img.save(os.path.join(post_static_path, 'banner.jpg'))
    post_images.thumbnail_img.save(os.path.join(post_static_path, 'thumbnail.jpg'))

    # Copy image files to the article's directory
    for img_path in article_imgs:
        # Ignore image links
        if img_path.startswith('http') or img_path.startswith('www'):
            continue 
        
        # Get absolute path to image
        abs_path = os.path.realpath(os.path.join(post_dir, img_path))

        if compress_imgs and not img_path.endswith('.gif'):
            if not quiet:
                print ('Converting {}'.format(abs_path))
            save_path = os.path.join(post_static_path, os.path.basename(abs_path)) #os.path.splitext(abs_path)[0] + '.jpg')  # TODO: CONVERT ALL IMAGES TO JPEG
            img = Image.open(abs_path)
            #img = img.convert('RGB')
            img.thumbnail(DEFAULT_IMG_SIZE, Image.ANTIALIAS)
            img.save(save_path)
        else:
            # Copy to the post's static directory
            copy_to_static(abs_path, post_static_path)
    
    # Write the html file to the article directory
    article_dest_path = os.path.join(post_static_path, slug) + '.html'
    with open(article_dest_path, 'w', encoding='utf-8', errors='strict') as html_file:
        html_file.write(article_html)

    # Add the file to the search engine's index.   # TODO: BREAK EACH OF THESE TASKS INTO A SEPARATE FUNCTION
    # We can index the Markdown file.
    search_index = index.connect(current_app.config['SEARCH_INDEX_PATH'])
    search_index.index_file(post_path, slug)
    
    if not quiet:
        print ('Retrieved from database, I got: {}'.format(database.get_post_by_slug(slug)[:]))
        confirm_input = 'n'
        while confirm_input != 'y':
            confirm_input = input('Commit changes? (y/n)').strip().lower()
            if confirm_input == 'n':
                # Delete the created folder and exit
                shutil.rmtree(post_static_path)
                print ('Aborted committing post. Files in the static folder have been deleted.')
                sys.exit(0)

    # Commit database changes
    database.commit()
    # Commit search engine index changes
    search_index.commit()


# upload_file: text file, each line has the slug of the post to upload.
# In one SFTP connection, copies the post folders to the remote.
# Then copies the database and search index.
# If a file with the same name exists, will run filecmp and abort if the files are identical.
@click.command('upload_posts')
@click.argument('upload_file')
@with_appcontext
def upload_posts(upload_file):
    with open(upload_file, 'r') as f:
        slugs = f.read().split()

    # Read the secret file to get host information
    try:
        with open(current_app.config['SECRET_PATH']) as secret_file:
            secret_data = json.load(secret_file)
            host = secret_data['host']
            username = secret_data['username']
            password = secret_data['password']
    except IOError:
        print ('No secret file found')
        host = input('Enter host: ').strip()
        username = input('Enter username: ').strip()
        password = input('Enter password: ').strip()

    print ('Initiating SFTP connection with {}...'.format(host))

    # Push files to PythonAnywhere, via SFTP
    # SFTP instructions for PythonAnywhere: https://help.pythonanywhere.com/pages/SSHAccess
    # From cmd, the following correctly copies the 'inventory-systems' folder to PythonAnywhere:
    # 'put -r flaskr/static/inventory-systems Stefans-Blog/flaskr/static/inventory-systems'
    with pysftp.Connection(host, username=username, password=password) as sftp:
        # Create post directory on host and copy post files
        with sftp.cd(r'/home/skussmaul/Stefans-Blog/flaskr/static'):
            for slug in slugs:
                # Path to local post folder
                local_dir = os.path.join(current_app.static_folder, slug)
                # Create post directory on remote
                try:
                    sftp.mkdir(slug)
                except IOError:
                    print ('Warning: The directory already exists')

                # Enter post directory
                with sftp.cd(slug):
                    # Copy all files from 'local_dir' to remote.
                    # This is a workaround because the 'put_d' (put directory) command is not working.
                    for file_to_copy in os.listdir(local_dir):
                        print ('Uploading {}...'.format(file_to_copy))
                        if sftp.isfile(file_to_copy):
                            print('File already exists')
                        else:
                            sftp.put(os.path.join(local_dir, file_to_copy))
        # Copy instance files
        with sftp.cd(r'/home/skussmaul/Stefans-Blog/instance'):
            sftp.put(current_app.config['DATABASE_PATH'])
            sftp.put(current_app.config['SEARCH_INDEX_PATH'])



def sync_to_production():
    return