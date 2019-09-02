import sys
sys.path.append('../flaskr')  # TODO: INCLUDE FLASKR USING AN __INIT__ IN THE PROJECT DIRECTORY. SEE https://stackoverflow.com/questions/4383571/importing-files-from-different-folder
import re
import os
import shutil
from datetime import date, datetime
import json
import markdown2 as md
#from flaskr.database import Database

# Path to the directory this script is being executed in 
this_dir = os.path.dirname(os.path.abspath(__file__))

# Path to the static folder.
# A new directory will be created in the static folder under this post's slug.
PATH_TO_STATIC = os.path.realpath(os.path.join(this_dir, '..', 'flaskr', 'static'))

# Path to the database.
PATH_TO_DATABASE = os.path.realpath(os.path.join(this_dir, '..', 'flaskr', 'instance', 'posts.db'))

# Keys used in post-meta.json
KEY_TITLE = 'title'
KEY_BYLINE = 'byline'
KEY_SLUG = 'slug'
KEY_DATE = 'date'
KEY_TAGS = 'tags'

# generates a slug given a string
# slugs are used to create urls
def generate_slug(string):
    return string.replace(' ', '-').replace(':', '').lower()

# find and return a list of all file names found in the markdown
# link/image references
def extract_filenames_from_md(md_string):
    file_names = []
    # iterate over link references
    for match in re.finditer(MD_REFERENCE_REGEX, md_string):
        link_ref = match.group(2)
        # ignore urls
        if not link_ref.startswith('http') and not link_ref.startswith('www'):
            file_names.append(link_ref)

    return file_names

# Takes the path to a Markdown file, read it, and renders it to HTML.
# Returns (rendered HTML as a string, list of image sources found in <img> tags).
# This function will render images as Bootstrap figures. TODO: EXPLAIN HOW TO ADD A CAPTION
def render_md_file(file_path):
    # Regex used to match custom "[figure]" lines
    figure_regex = re.compile(r'\[figure: ([^,]+), ([^\]]+)]')
    line_html = ''
    html_snippets = []
    images = []
    # print ('Reading file...')
    with open(file_path, 'r', encoding='utf8') as md_file:
        for line in md_file:
            # print ('>>{}'.format(line))
            figure_match = figure_regex.match(line)
            # Handle figures
            if figure_match:
                # print ('Got a match')
                img_path = figure_match.group(1)
                img_caption = figure_match.group(2)
                print (img_path, img_caption)
                # TODO: HANDLE alt, and make this string a constant (?)
                line_html = \
r'''<figure class="figure">
    <img src="{}" class="figure-img img-fluid rounded" alt="">
    <figcaption class="figure-caption text-right">{}</figcaption>
</figure>'''.format(img_path, img_caption)
                images.append(img_path)
            # Handle standard Markdown->HTML
            else:
                line_html = md.markdown(line)
  
            html_snippets.append(line_html)

    return ''.join(html_snippets), images

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
    meta_path = os.path.join(post_dir, 'post-meta.json')
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

    # Read and process the post Markdown file 
    try:
        article_html, article_imgs = render_md_file(post_path)
        print (article_html)
        print (article_imgs)
    except IOError:
        print ('ERROR: Could not read the post file ("{}")'.format(post_path))
        sys.exit()
  
    # Make sure title is defined
    if KEY_TITLE not in post_data:
        print ('ERROR: post-meta.json must contain a "{}" field'.format(KEY_TITLE))
        sys.exit()
    title = post_data[KEY_TITLE]

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
        byline = md_post_text[:200]

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

    print ([title, byline, slug, post_date])
'''
    # Get connection to the post database
    database = Database(PATH_TO_DATABASE)

    # Add post to the database.
    # This will fail if there is a problem with the post data
    database.add_post(title, byline, slug, post_date)

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
    # get path where the post data will live
    post_static_path = os.path.join(PATH_TO_STATIC, slug)

    # create the directory
    try:
        os.mkdir(post_static_path)
    except FileExistsError:  # TODO: THROW VALUEERROR
        print ('Post directory already exists')

    # copy local files to the post's folder
    # also update their positions in the html
    for filename in files_to_copy:
        src_path = os.path.join(post_dir, filename)
        dest_path = os.path.join(post_static_path, filename)
        print ('copying {} to {}'.format(src_path, dest_path))
        shutil.copyfile(src_path, dest_path)

    # correct file refs in the html
    for filename in files_to_copy:
        file_url = os.path.join('/static', slug, filename)
        print ('Replacing {} with {}'.format(filename, file_url))
        html_post_text = html_post_text.replace(filename, file_url)

    # write the html file to the post's directory
    post_html_path = os.path.join(post_static_path, slug) + '.html'
    with open(post_html_path, 'w') as html_file:
        html_file.write(html_post_text)

    print ('Retrieved from database, I got: {}'.format(database.get_post_by_slug(slug)[:]))
    print ('5 most recent: {}'.format(database.get_recent_posts(5)[:]))


    database.commit()
'''