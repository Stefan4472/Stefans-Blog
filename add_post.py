import sys  # TODO: PUT THIS IN ITS OWN FOLDER? USE CLICK TO MAKE IT INTO A FLASK COMMAND?
import re
import os
import shutil
import pysftp
from datetime import date, datetime
from PIL import Image
import json
import markdown2 as md
import randomcolor
from flaskr.database import Database
import flaskr.search_engine.index as index  # TODO: BETTER IMPORTS

# Path to the directory this script is being executed in 
this_dir = os.path.dirname(os.path.abspath(__file__))

# Path to the static folder.
# A new directory will be created in the static folder under this post's slug.
# Note that this can handle relative paths, including those that start with '../'
PATH_TO_STATIC = os.path.realpath(os.path.join(this_dir, 'flaskr', 'static'))
# Path to the database.
PATH_TO_DATABASE = os.path.realpath(os.path.join(this_dir, 'instance', 'posts.db'))
# Path to the search engine's index file.
PATH_TO_INDEX = os.path.realpath(os.path.join(this_dir, 'instance', 'index.json'))
# Path to the secret file YES I KNOW IT SHOULDN'T BE A PLAIN TEXT FILE!!!
PATH_TO_SECRET = os.path.realpath(os.path.join(this_dir, 'instance', 'secret.txt'))

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
THUMBNAIL_SIZE = (640, 640)

# generates a slug given a string
# slugs are used to create urls
def generate_slug(string):
    return string.replace(' ', '-').replace(':', '').lower()

def get_static_url(filepath):
    return '{{{{ url_for(\'static\', filename=\'{}\') }}}}'.format(filepath)

def generate_random_color():
    return COLOR_GENERATOR.generate(luminosity='light', count=1)[0]  # TODO: USE 'light' or 'bright' LUMINOSITY?

# Takes the path to a Markdown file, read it, and renders it to HTML.
# Returns (rendered HTML as a string, list of image sources found in <img> tags).
# This function will render images as Bootstrap figures. TODO: EXPLAIN HOW TO ADD A CAPTION
def render_md_file(file_path, img_save_dir):
    # Regex used to match custom "[figure]" lines
    figure_regex = re.compile(r'\[figure: ([^,]+), ([^\]]+)]')
    html_snippets = []
    images = []
    md_text = ''
    last_match_index = 0

    # print ('Reading file...')
    with open(file_path, 'r', encoding='utf8') as md_file:
        md_text = md_file.read()
    
    # Iterate through '[figure: ]' instances, which must be handled specially.
    # Everything else can be rendered using the 'markdown' library.
    for figure_match in re.finditer(figure_regex, md_text):
        start = figure_match.start()
        end = figure_match.end()
        
        # Render the Markdown between the end of the last figure match and the start of
        # this figure match
        if start != last_match_index + 1:
            rendered_html = md.markdown(md_text[last_match_index + 1 : start], extras=['fenced-code-blocks'])
            html_snippets.append(rendered_html)
            #print (rendered_html)
        
        # Render the figure
        img_path = figure_match.group(1)
        img_caption = figure_match.group(2)
        # print (img_path, img_caption)
        img_url = get_static_url(img_save_dir + '/' + os.path.basename(img_path))  # TODO: CLEAN UP
        # print ('url is {}'.format(img_url))
        # TODO: HANDLE alt, and make this string a constant (?)
        # TODO: ANY WAY TO MAKE THE BACKGROUND COLOR OF THE CAPTION GRAY, AND LIMIT IT TO THE WIDTH OF THE TEXT?
        rendered_html = \
r'''<figure class="figure text-center">
<img src="{}" class="figure-img img-fluid rounded" alt="">
<figcaption class="figure-caption" style="background-color: red;"><em>{}</em></figcaption>
</figure>'''.format(img_url, img_caption)
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

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print ('ERROR: Expected an argument, /abs/path/to/post/folder')
        sys.exit()

    post_dir = sys.argv[1]
    print ('Got post directory "{}"'.format(post_dir))

    # Ensure the provided path is a directory that exists 
    if not os.path.isdir(post_dir):
        print ('ERROR: The provided path is not a directory or does not exist')
        sys.exit()

    # Determine absolute path to the post file and the metadata file
    post_path = os.path.join(post_dir, 'post.md')
    meta_path = os.path.join(post_dir, 'post-meta.json')

    post_markdown = ''
    post_html = ''
    post_data = {}

    # Read the metadata file
    try:
        with open(meta_path, 'r') as meta_file:
            post_data = json.load(meta_file)
    except IOError:
        print ('ERROR: Could not read the meta-data file ("{}")'.format(meta_path))
        sys.exit()

    # Read the Markdown file 
    try:
        with open(post_path, 'r', encoding='utf8') as post_file:
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
        post_img = Image.open(post_img_path)
    else:
        print ('ERROR: post-meta.json must contain a "{}" field'.format(KEY_IMAGE))
        sys.exit()

    # Get banner image
    if KEY_BANNER in post_data:
        post_banner_path = os.path.realpath(os.path.join(post_dir, post_data[KEY_BANNER]))
        post_banner = Image.open(post_banner_path)
    else:
        print ('ERROR: post-meta.json must contain a "{}" field'.format(KEY_BANNER))
        sys.exit()

    if KEY_THUMBNAIL in post_data:
        post_thumbnail_path = os.path.realpath(os.path.join(post_dir, post_data[KEY_THUMBNAIL]))
        post_thumbnail = Image.open(post_thumbnail_path)
    else:
        # No thumbnail specified: load the post's image. It will be made into 
        # a thumbnail later
        post_thumbnail = Image.open(post_img_path)

    # Build URLs for the image, banner, and thumbnail.
    # They will have prescribed filenames ('image', 'banner', 'thumbnail') and will be    # TODO: NEED ACCESS TO URL_FOR()
    # converted to JPG
    post_img_url = '/static/{}/featured_img.jpg'.format(slug)  #url_for('static', filename=slug + '/' + 'featured_img.jpg')
    post_banner_url = '/static/{}/banner.jpg'.format(slug)  #url_for('static', filename=slug + '/' + 'banner.jpg')
    post_thumbnail_url = '/static/{}/thumbnail.jpg'.format(slug)  #url_for('static', filename=slug + '/' + 'thumbnail.jpg')

     # Get connection to the post database
    database = Database(PATH_TO_DATABASE)

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
    post_static_path = os.path.join(PATH_TO_STATIC, slug)

    # Create the directory for the post data
    try:
        os.mkdir(post_static_path)
    except FileExistsError:
        pass
        #print ('ERROR: Post directory already exists')
        #sys.exit(0)

    # Render the Markdown file to HTML
    article_html, article_imgs = render_md_file(post_path, slug)  # TODO: IS THIS HANDLING BLANK LINES CORRECTLY?

    # For the following images: convert to RGB, resize, and save as JPEG
    # Size and save the post's featured image 
    post_img = post_img.convert('RGB').resize(FEATURED_IMG_SIZE, Image.ANTIALIAS)
    post_img.save(os.path.join(post_static_path, 'featured_img.jpg'), 'JPEG')
    # Size and save the post's banner image 
    post_banner = post_banner.convert('RGB').resize(BANNER_SIZE, Image.ANTIALIAS)
    post_banner.save(os.path.join(post_static_path, 'banner.jpg'), 'JPEG')
    # Size and save the post's thumbnail
    post_thumbnail = post_thumbnail.convert('RGB')
    post_thumbnail.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)
    post_thumbnail.save(os.path.join(post_static_path, 'thumbnail.jpg'), 'JPEG')

    # Copy image files to the article's directory
    for img_path in article_imgs:
        # Ignore image links
        if img_path.startswith('http') or img_path.startswith('www'):
            continue 
        
        # Get absolute path to image
        abs_path = os.path.realpath(os.path.join(post_dir, img_path))
        # Copy to the post's static directory
        copy_to_static(abs_path, post_static_path)
    
    # Write the html file to the article directory
    article_dest_path = os.path.join(post_static_path, slug) + '.html'
    with open(article_dest_path, 'w') as html_file:
        html_file.write(article_html)

    # Add the file to the search engine's index.   # TODO: BREAK EACH OF THESE TASKS INTO A SEPARATE FUNCTION
    # We can index the Markdown file.
    search_index = index.connect(PATH_TO_INDEX)
    search_index.index_file(post_path, slug)
    
    print ('Retrieved from database, I got: {}'.format(database.get_post_by_slug(slug)[:]))

    while True:
        confirm_input = input('Commit changes? (y/n)').strip().lower()
        if confirm_input == 'y':
            # Commit database changes
            database.commit()
            # Commit search engine index changes
            search_index.commit()

            upload_input = input('Upload additions to server? (y/n)').strip().lower()
            if upload_input == 'y':
                # Read the secret file to get host information
                try:
                    with open(PATH_TO_SECRET) as secret_file:
                        secret_data = json.load(secret_file)
                        host = secret_data['host']
                        username = secret_data['username']
                        password = secret_data['password']
                except IOError:
                    print ('No secret file found')
                    host = input('Enter host: ').strip()
                    username = input('Enter username: ').strip()
                    password = input('Enter password: ').strip()

                print (host, username, password)
                input()
                # Push files to host, via SFTP
                with pysftp.Connection(host, username=username, password=password) as sftp:
                    print (sftp.listdir())
                    input()
                    with sftp.cd(r'/home/skussmaul/Stefans-Blog/flaskr/static'):
                        print (sftp.listdir())
                        input()
                        # Create post directory on host
                        sftp.mkdir(slug)
                        print (sftp.listdir())
                        input()
                        with sftp.cd(slug):
                            # Copy post data directory to host
                            sftp.put_d(post_static_path)
                            print (sftp.listdir())
                    input()
                    with sftp.cd(r'/home/skussmaul/Stefans-Blog/flaskr/instance'):
                        # Copy instance files
                        sftp.put(PATH_TO_DATABASE)
                        sftp.put(PATH_TO_INDEX)
                    input()
                #  print (sftp.listdir())
                #     input()
                #     # Path to the post directory, on host
                #     post_host_path = r'/home/skussmaul/Stefans-Blog/flaskr/static/{}'.format(slug)
                #     # Create post directory on host
                #     sftp.mkdir(post_host_path)
                #     # Copy post data directory to host
                #     sftp.put_d(post_static_path, post_host_path)
                #     # Copy instance files
                #     sftp.put(PATH_TO_DATABASE, remotepath=r'/home/skussmaul/Stefans-Blog/instance/posts.db')
                #     sftp.put(PATH_TO_INDEX, remotepath=r'/home/skussmaul/Stefans-Blog/instance/index.json')
            break
        elif confirm_input == 'n':
            # Delete the created folder and exit
            shutil.rmtree(post_static_path)
            print ('Aborted committing post. Files in the static folder have been deleted.')
            sys.exit(0)
        else:
            print ('Not a valid input')

    # TODO: PUSH NEW/UPDATED FILES TO THE SERVER