import sys  # TODO: PUT THIS IN ITS OWN FOLDER? USE CLICK TO MAKE IT INTO A FLASK COMMAND?
import re
import os
import shutil
from datetime import date, datetime
import json
import markdown2 as md
from flaskr.database import Database
from flaskr.search_engine.index import Index, restore_index_from_file  # TODO: BETTER IMPORTS

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

# Keys used in post-meta.json
KEY_TITLE = 'title'
KEY_BYLINE = 'byline'
KEY_SLUG = 'slug'
KEY_DATE = 'date'
KEY_TAGS = 'tags'
KEY_IMAGE = 'image'

# generates a slug given a string
# slugs are used to create urls
def generate_slug(string):
    return string.replace(' ', '-').replace(':', '').lower()

def get_static_url(filepath):
    return '{{{{ url_for(\'static\', filename=\'{}\') }}}}'.format(filepath)

# Takes the path to a Markdown file, read it, and renders it to HTML.
# Returns (rendered HTML as a string, list of image sources found in <img> tags).
# This function will render images as Bootstrap figures. TODO: EXPLAIN HOW TO ADD A CAPTION
def render_md_file(file_path, img_save_dir):
    # Regex used to match custom "[figure]" lines
    figure_regex = re.compile(r'\[figure: ([^,]+), ([^\]]+)]')
    line_html = ''
    html_snippets = []
    images = []
    # print ('Reading file...')
    with open(file_path, 'r', encoding='utf8') as md_file:
        for line in md_file:
            # Ignore blank lines
            if not line:
                print ('Ignoring a blank line')
                continue
            # print ('>>{}'.format(line))
            figure_match = figure_regex.match(line)
            # Handle figures
            if figure_match:
                # print ('Got a match')
                img_path = figure_match.group(1)
                img_caption = figure_match.group(2)

                print (img_path, img_caption)
                img_url = get_static_url(img_save_dir + '/' + os.path.basename(img_path))  # TODO: CLEAN UP
                print ('url is {}'.format(img_url))
                # TODO: HANDLE alt, and make this string a constant (?)
                line_html = \
r'''<figure class="figure">
    <img src="{}" class="figure-img img-fluid rounded" alt="">
    <figcaption class="figure-caption text-center">{}</figcaption>
</figure>'''.format(img_url, img_caption)
                images.append(img_path)
            # Handle standard Markdown->HTML
            else:
                line_html = md.markdown(line)
  
            html_snippets.append(line_html)

    return ''.join(html_snippets), images

def copy_to_static(file_path, static_path):  # TODO: IMPROVE
    # Make sure the file exists
    if not (os.path.exists(file_path) and os.path.isfile(file_path)):
        print ('ERROR: The image path "{}" is not a real file')  # TODO: RAISE EXCEPTION
        return

    # Build destination path for the image
    dest_path = os.path.join(static_path, os.path.basename(file_path))
    print (dest_path)
    
    # Copy the image to the folder
    shutil.copyfile(file_path, dest_path)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print ('ERROR: Expected an argument, /abs/path/to/post/folder')
        sys.exit()

    post_dir = sys.argv[1]
    print ('got post_dir {}'.format(post_dir))

    # Ensure the provided path is a directory that exists 
    if not os.path.isdir(post_dir):
        print ('ERROR: The provided path is not a directory or does not exist')
        sys.exit()

    # Determine absolute path to the post file and the meta file
    post_path = os.path.join(post_dir, 'post.md')
    meta_path = os.path.join(post_dir, 'post-meta.json')  # TODO: CONSISTENT USAGE OF EITHER 'POST' OR 'ARTICLE'
    print (post_path, meta_path)

    md_post_text = ''
    html_post_text = ''
    post_data = {}

    # Read the meta-data file
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
            print('ERROR: Byline cannot be more than 200 characters long')
            sys.exit()     
    else:
        # Default byline is the first 200 chars of the post
        # TODO: GET THE FIRST PARAGRAPH
        byline = post_markdown[:200]

    # Get slug
    if KEY_SLUG in post_data:
        slug = post_data[KEY_SLUG]
    else:
        # Generate slug from title if needed
        slug = generate_slug(title)

    # Get publish date
    # TODO: CONVERT TO DATE AND VALIDATE
    if KEY_DATE in post_data:
        post_date = post_data[KEY_DATE]
    else:  
        # Default to today's date
        post_date = date.today()

    if KEY_IMAGE in post_data:
        post_img = post_data[KEY_IMAGE]
    else:
        print ('ERROR: post-meta.json must contain a "{}" field'.format(KEY_IMAGE))
        sys.exit()
    post_img_name = 'post-image' + os.path.splitext(post_img)[1]
    print ([title, byline, slug, post_date, post_img])
    
     # Get connection to the post database
    database = Database(PATH_TO_DATABASE)

    # Add post to the database.
    # This will fail if there is a problem with the post data
    database.add_post(title, byline, slug, post_date, post_img_name)

    if KEY_TAGS in post_data:
        tags = post_data[KEY_TAGS]

    # Add tags to the database
    for tag in tags:
        print ('Handling tag {}'.format(tag))
        tag_slug = generate_slug(tag)
        # Add tag to the database if not already there
        if not database.has_tag(tag_slug):
            database.add_tag(tag, tag_slug)
        # Add post->tag mapping to database
        database.add_tag_to_post(tag_slug, slug)
    
    # TODO: VALIDATE?
    
    # Get path to where the article data will live ('/static/[slug]')
    post_static_path = os.path.join(PATH_TO_STATIC, slug)

    # Create the directory for the article data
    try:
        os.mkdir(post_static_path)
    except FileExistsError:  # TODO: THROW VALUEERROR
        pass
        #print ('ERROR: Post directory already exists')
        #sys.exit(0)

    # Render the Markdown file to HTML
    article_html, article_imgs = render_md_file(post_path, slug)
    print (article_html)
    print (article_imgs)

    # Get absolute path to the post image
    img_abs_path = os.path.realpath(os.path.join(post_dir, post_img))
    
    # Make sure the image exists
    if not (os.path.exists(img_abs_path) and os.path.isfile(img_abs_path)):
        print ('ERROR: The image path "{}" is not a real file'.format(img_abs_path))  # TODO: RAISE EXCEPTION
        sys.exit(0)

    # Build absolute path for the post image in the static directory
    img_dest_path = os.path.join(post_static_path, post_img_name)
    print (img_dest_path)
    # Copy the post image to the post directory 
    shutil.copyfile(img_abs_path, img_dest_path)

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
    print (article_dest_path)
    with open(article_dest_path, 'w') as html_file:
        html_file.write(article_html)

    # Add the file to the search engine's index.   # TODO: BREAK EACH OF THESE TASKS INTO A SEPARATE FUNCTION
    # We can index the Markdown file.
    search_index = restore_index_from_file(PATH_TO_INDEX)
    search_index.index_file(post_path, slug)
    
    print ('Retrieved from database, I got: {}'.format(database.get_post_by_slug(slug)[:]))

    while True:
        confirm_input = input('Commit changes? (y/n)').strip().lower()
        if confirm_input == 'y':
            # Commit database changes
            database.commit()
            # Commit search engine index changes
            search_index.save_to_file(PATH_TO_INDEX)
            break
        elif confirm_input == 'n':
            # Delete the created folder and exit
            shutil.rmtree(post_static_path)
            print ('Aborted committing post. Files in the static folder have been deleted.')
            sys.exit(0)
        else:
            print ('Not a valid input')

    # TODO: UPDATE SEARCH ENGINE INDEX
    # TODO: PUSH NEW FILES TO THE SERVER