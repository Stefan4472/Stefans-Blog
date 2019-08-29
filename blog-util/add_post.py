import sys
import re
import os
import shutil
from datetime import date, datetime
import json
import markdown2 as md
#from stefanonsoftware.database import Database

# Path to the directory this script is being executed in 
this_dir = os.path.dirname(os.path.abspath(__file__))

# Relative path to flask's static folder.
# A new directory will be created in the static folder under this post's slug.
PATH_TO_STATIC = os.path.realpath(os.path.join(this_dir, '..', 'flaskr', 'static'))
PATH_TO_DATABASE = os.path.realpath(os.path.join(this_dir, '..', 'flaskr', 'instance', 'posts.db'))

# keys used in post-meta.json
KEY_TITLE = 'title'
KEY_BYLINE = 'byline'
KEY_SLUG = 'slug'
KEY_DATE = 'date'
KEY_TAGS = 'tags'

print (PATH_TO_DATABASE)
print (PATH_TO_STATIC)
'''
# matches a reference tag in markdown
MD_REFERENCE_REGEX = re.compile(r'\[(.*?)\]: (\S+)')

# generate's a slug given a string
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

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print ('Expected an argument, /abs/path/to/post/folder')
        sys.exit()

    post_dir = sys.argv[1]
    print ('got post_dir {}'.format(post_dir))
    # TODO: ENSURE IT'S A VALID DIR

    post_path = os.path.join(post_dir, 'post.md')
    meta_path = os.path.join(post_dir, 'post-meta.json')
    print (post_path, meta_path)

    md_post_text = ''
    html_post_text = ''

    # read the post file and convert to html
    with open(post_path, 'r', encoding='utf8') as post_file:
        md_post_text = post_file.read()

    # handle files in the markdown
    files_to_copy = extract_filenames_from_md(md_post_text)
    print (files_to_copy)

    html_post_text = md.markdown(md_post_text)

    print (html_post_text)

    post_data = {}
    # read the meta-data file and generate values
    with open(meta_path, 'r') as meta_file:
        post_data = json.load(meta_file)

    # make sure title is defined
    if KEY_TITLE not in post_data:
        raise ValueError('post-meta.json must contain a "{}" field'.format(KEY_TITLE))
    title = post_data[KEY_TITLE]

    # make sure biline is not more than 200 characters
    if KEY_BYLINE in post_data:
        if len(post_data[KEY_BYLINE]) > 200:
            raise ValueError('Biline cannot be more than 200 chars long')
        byline = post_data[KEY_BYLINE]
    # default byline is the first 200 chars of the post
    # TODO: GET THE FIRST PARAGRAPH
    else:
        byline = md_post_text[:200]

    # generate slug from title if needed
    if KEY_SLUG in post_data:
        slug = post_data[KEY_SLUG]
    else:
        slug = generate_slug(post_data[KEY_TITLE])

    # TODO: CONVERT TO DATE AND VALIDATE
    if KEY_DATE in post_data:
        post_date = post_data[KEY_DATE]
    else:
        post_date = date.today()

    print ([title, byline, slug, post_date])

    # get connection to the post database
    database = Database(PATH_TO_DATABASE)

    # add post to the database
    # this will fail if there is a problem with the post data
    database.add_post(title, byline, slug, post_date)

    if KEY_TAGS in post_data:
        tags = post_data[KEY_TAGS]

    # add tags to the database
    for tag in tags:
        print ('Handling tag {}'.format(tag))
        tag_slug = generate_slug(tag)
        # add tag to the database if not already there
        if not database.has_tag(tag_slug):
            database.add_tag(tag, tag_slug)
        # add mapping to database
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