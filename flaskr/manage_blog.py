import sys  # TODO: PUT THIS IN ITS OWN FOLDER? USE CLICK TO MAKE IT INTO A FLASK COMMAND?
import re
import os
import shutil
import click
import pysftp
from datetime import date, datetime
from flask import current_app, url_for
from flask.cli import with_appcontext
from PIL import Image
import json
import markdown2 as md
import randomcolor
from flaskr.database import Database
import flaskr.search_engine.index as index  # TODO: BETTER IMPORTS

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
FEATURED_IMG_SIZE = (2000, 1080)
# Prescribed banner size
BANNER_SIZE = (1440, 600) # (1928, 768)
# Size of image thumbnails
THUMBNAIL_SIZE = (800, 600)

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

# Takes the path to a Markdown file, read it, and renders it to HTML.
# Returns (rendered HTML as a string, list of image sources found in <img> tags).
# This function will render images as Bootstrap figures. TODO: EXPLAIN HOW TO ADD A CAPTION
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
    <img src="{}" class="figure-img img-fluid" style="max-width: 100%; height: auto;" alt="">
    <figcaption class="figure-caption" style="background-color: #EEEEEE;"><em>{}</em></figcaption>
</figure>

'''.format(img_url, img_caption)
        # Render without caption
        else:
            rendered_html = \
'''
<figure class="figure text-center">
    <img src="{}" class="figure-img img-fluid" style="max-width: 100%; height: auto;" alt="">
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
        print ('ERROR: The image path "{}" is not a real file')  # TODO: RAISE EXCEPTION
        return

    # Build destination path for the image
    dest_path = os.path.join(static_path, os.path.basename(file_path))
    # print (dest_path)
    
    # Copy the image to the folder
    shutil.copyfile(file_path, dest_path)

@click.command('add_post')
@click.argument('post_dir')
@click.option('--upload', is_flag=True, default=False, help='Whether to upload the post to PythonAnywhere')
@click.option('--quiet', is_flag=True, default=False, help='Whether to suppress print statements and confirmation promts')
@click.option('--compress_imgs', is_flag=True, default=True, help='Whether to resize images to {} and convert to JPG'.format(DEFAULT_IMG_SIZE))
@with_appcontext
def add_post(post_dir, upload, quiet, compress_imgs):
    print('\n{}'.format(post_dir))
    # If provided path is not a directory, treat it as a relative path from
    # the path the script was executed from
    if not os.path.isdir(post_dir):
        post_path = os.path.realpath(os.path.join(sys.argv[0], post_dir))

    # Ensure the provided path is a directory that exists 
    if not os.path.isdir(post_dir):
        print ('ERROR: The provided path is not a directory or does not exist')
        sys.exit()

    if not quiet:
        print ('Got post directory "{}"'.format(post_dir))
    
    # Determine absolute path to the post file and the metadata file
    post_path = os.path.join(post_dir, 'post.md')
    meta_path = os.path.join(post_dir, 'post-meta.json')

    post_markdown = ''
    post_html = ''
    post_data = {}

    # Read the metadata file
    try:
        with open(meta_path, 'r', encoding='utf-8', errors='strict') as meta_file:
            post_data = json.load(meta_file)
    except IOError:
        print ('ERROR: Could not read the meta-data file ("{}")'.format(meta_path))
        sys.exit()

    # Read the Markdown file 
    try:
        with open(post_path, 'r', encoding='utf-8', errors='strict') as post_file:
            post_markdown = post_file.read()
    except IOError:
        print ('ERROR: Could not read the post file ("{}")'.format(post_path))
        sys.exit()

    # Make sure title is defined
    if KEY_TITLE in post_data:
        title = post_data[KEY_TITLE]
    else:
        print ('ERROR: post-meta.json must contain a "{}" field'.format(KEY_TITLE))
        sys.exit()

    # Get byline
    if KEY_BYLINE in post_data:
        byline = post_data[KEY_BYLINE]
        # Make sure byline is not more than 200 characters
        if len(byline) > 200:
            if not quiet:
                print ('Trimming byline to 200 characters')
            byline = byline[:200]
    else:
        # Just take the first 200 characters of Markdown
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

    # Get post image
    if KEY_IMAGE in post_data:
        post_img_path = os.path.realpath(os.path.join(post_dir, post_data[KEY_IMAGE]))
        post_img_type = os.path.splitext(post_img_path)[1]
        post_img = Image.open(post_img_path)
    else:
        print ('ERROR: post-meta.json must contain a "{}" field'.format(KEY_IMAGE))
        sys.exit()

    # Get banner image
    if KEY_BANNER in post_data:
        post_banner_path = os.path.realpath(os.path.join(post_dir, post_data[KEY_BANNER]))
        post_banner_type = os.path.splitext(post_banner_path)[1]
        post_banner = Image.open(post_banner_path)
    else:
        # No banner specified: use the post's image, which will be resized later
        post_banner_type = post_img_type
        post_banner = post_img.copy()

    if KEY_THUMBNAIL in post_data:
        post_thumbnail_path = os.path.realpath(os.path.join(post_dir, post_data[KEY_THUMBNAIL]))
        post_thumbnail_type = os.path.splitext(post_thumbnail_path)[1]
        post_thumbnail = Image.open(post_thumbnail_path)
    else:
        # No thumbnail specified: load the post's image, which will be resized later
        post_thumbnail_type = post_img_type
        post_thumbnail = post_img.copy()

    # Build URLs for the image, banner, and thumbnail.
    # They will have prescribed filenames ('image', 'banner', 'thumbnail') 
    post_img_url = current_app.static_url_path + '/' + slug + '/featured_img' + post_img_type
    post_banner_url = current_app.static_url_path + '/' + slug + '/banner' + post_banner_type
    post_thumbnail_url = current_app.static_url_path + '/' + slug + '/thumbnail' + post_thumbnail_type
    
    # Get connection to the post database
    database = Database(current_app.config['DATABASE_PATH'])

    # Add post to the database.
    # This will fail if there is a problem with the post data
    database.add_post(title, byline, slug, post_date, post_img_url, post_banner_url, post_thumbnail_url)

    if KEY_TAGS in post_data:
        tags = post_data[KEY_TAGS]
        # Add tags to the database
        for tag in tags:
            # print ('Handling tag {}'.format(tag))
            tag_slug = generate_slug(tag)
            tag_color = generate_random_color()
            # Add tag to the database if not already there
            if not database.has_tag(tag_slug):
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
                    print('No changes made')
                    sys.exit(0)

    # Render the Markdown file to HTML  NOTE: THE FILE HAS ALREADY BEEN READ!
    article_html, article_imgs = render_md_file(post_path, slug)  # TODO: IS THIS HANDLING BLANK LINES CORRECTLY?
    
    # For the following images: convert to RGB, resize, and save as JPEG
    # Size and save the post's featured image 
    post_img = post_img.resize(FEATURED_IMG_SIZE, Image.ANTIALIAS)  # TODO: THUMBNAIL
    post_img.save(os.path.join(post_static_path, 'featured_img' + post_img_type))
    # Size and save the post's banner image 
    post_banner = post_banner.resize(BANNER_SIZE, Image.ANTIALIAS)
    post_banner.save(os.path.join(post_static_path, 'banner' + post_banner_type))
    # Size and save the post's thumbnail
    # post_thumbnail = post_thumbnail.convert('RGB')
    post_thumbnail.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)
    post_thumbnail.save(os.path.join(post_static_path, 'thumbnail' + post_thumbnail_type))

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

    if upload:
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

        if not quiet:
            print ('Initiating SFTP connection with {}...'.format(host))

        # Push files to PythonAnywhere, via SFTP
        # SFTP instructions for PythonAnywhere: https://help.pythonanywhere.com/pages/SSHAccess
        # From cmd, the following correctly copies the 'inventory-systems' folder to PythonAnywhere:
        # 'put -r flaskr/static/inventory-systems Stefans-Blog/flaskr/static/inventory-systems'
        with pysftp.Connection(host, username=username, password=password) as sftp:
            # Create post directory on host and copy post files
            with sftp.cd(r'/home/skussmaul/Stefans-Blog/flaskr/static'):
                # Create post directory on host
                try:
                    sftp.mkdir(slug)
                except IOError:
                    print ('Warning: The directory already exists')
                # Enter post directory
                with sftp.cd(slug):
                    # Copy all files in 'post_static_path' to host.
                    # This is a workaround because the 'put_d' (put directory) command is not working.
                    for file_to_copy in os.listdir(post_static_path):
                        if not quiet:
                            print ('Uploading {}...'.format(file_to_copy))
                        sftp.put(os.path.join(post_static_path, file_to_copy))
            # Copy instance files
            with sftp.cd(r'/home/skussmaul/Stefans-Blog/instance'):
                sftp.put(current_app.config['DATABASE_PATH'])
                sftp.put(current_app.config['SEARCH_INDEX_PATH'])