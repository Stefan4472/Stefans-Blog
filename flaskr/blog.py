import os
import click
from flask import (
    Blueprint, flash, g, redirect, render_template, render_template_string,
    request, url_for, current_app
)
from flask.cli import with_appcontext
from werkzeug.exceptions import abort
from flaskr.database import get_db
from flaskr.site_logger import log_visit
import flaskr.search_engine.index as index  # TODO: IMPROVE IMPORTS
import flaskr.featured_posts as fp
from functools import wraps

bp = Blueprint('blog', __name__)

# Decorator that logs the url being accessed.
# Simply calls 'log_visit()'.
def logged_visit(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        log_visit()
        return f(*args, **kwargs)
    return decorated_function

# # Registers a command-line function to initialize the search engine index.
# # Run using "python -m flask init-search-engine"
# @click.command('init-search-index')
# @with_appcontext
# def init_search_index_command():
#     # Wipe the index file  TODO: THIS WILL FAIL IF THE INDEX DOESN'T EXIST
#     open(current_app.config['SEARCH_INDEX_FILE'], 'w').close()
#     click.echo('Initialized the search engine index.')


@bp.route('/')
@logged_visit
def index():
    db = get_db()
    # Retrieve recent and featured posts
    recent_posts = db.get_recent_posts(5)
    featured_posts = [db.get_post_by_slug(slug) for slug in fp.get_featured_posts()]
   
    # Create dict mapping post_slug -> list of tags
    tags = { post['post_slug']: db.get_tags_by_post_slug(post['post_slug']) \
             for post in recent_posts + featured_posts }
    return render_template('blog/index.html', featured_posts=featured_posts, \
                            recent_posts=recent_posts, tags=tags)

@bp.route('/posts')
@logged_visit
def posts_page():
    db = get_db()
    query = request.args.get('query')

    # Get the optional search query, if present, and perform the search
    if query:
        # print ('Got query {}'.format(query))
        search_results = current_app.search_engine.search(query)
        # print ('Got the slugs {}'.format(search_results))
        posts = [db.get_post_by_slug(result_slug) for result_slug, _ in search_results]
        # print ('Got the posts {}'.format(posts))
    # Otherwise, get all posts
    else:
        posts = db.get_all_posts()

    # Retrieve tag data
    tags = { post['post_slug']: db.get_tags_by_post_slug(post['post_slug']) \
             for post in posts }

    # Render and return
    return render_template('blog/posts.html', search_query=query, posts=posts, tags=tags)

@bp.route('/post/<slug>')
@logged_visit
def post_view(slug):
    # print ('Looking up {}'.format(slug))
    db = get_db()
    # retrieve post data
    post = db.get_post_by_slug(slug)
    if not post:
        abort(404)

    # load post html TODO: FIGURE OUT HOW TO NOT HARDCODE THIS
    # THIS IS ACTUALLY NOT A STRAIGHTFORWARD THING TO FIX (AND ALSO NOT REALLY IMPORTANT FOR NOW)
    static_dir = 'static' #url_for('static', filename='')
    html_path = os.path.join(static_dir, slug, slug + '.html')
    post_html = ''
    with bp.open_resource(html_path, mode='r') as post_file:
        post_html = render_template_string(post_file.read())

    # retrieve data for the posts before and after
    prev_post = db.get_post_by_postid(post['post_id'] - 1)
    next_post = db.get_post_by_postid(post['post_id'] + 1)

    # retrieve tags this post is tagged under
    tags = db.get_tags_by_post_slug(slug)

    # Retrieve the path to the post's image
    post_image = url_for('static', filename=slug + '/' + post['post_image'])
    print (post_image)

    # TODO: SOME KIND OF FORMAT_TAG MACRO
    return render_template('blog/post.html', post=post, tags=tags, \
        post_html=post_html, image_url=post_image, prev_post=prev_post, \
        next_post=next_post)

# show post widgets for all posts under the given tag
@bp.route('/tag/<slug>')
@logged_visit
def tag_view(slug):
    db = get_db()
    if not db.has_tag(slug):
        abort(404)
    tag_title = db.get_tag_by_tagslug(slug)['tag_title']
    posts = db.get_posts_by_tag_slug(slug)
    return render_template('blog/tag_view.html', posts=posts, \
        tag_title=tag_title)

@bp.route('/portfolio')
@logged_visit
def portfolio_page():
    return render_template('blog/portfolio.html')

@bp.route('/about')
@logged_visit
def about_page():
    return render_template('blog/about.html')

@bp.route('/highlights')
@logged_visit
def highlights_page():
    return render_template('blog/highlights.html')

@bp.errorhandler(404)
@logged_visit
def error_page(error):
    return render_template('blog/404.html'), 404

