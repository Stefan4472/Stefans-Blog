import os
import click
from flask import (
    Blueprint, flash, g, redirect, render_template, render_template_string,
    request, url_for, current_app
)
from flask.cli import with_appcontext
from werkzeug.exceptions import abort
from . import database_context
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

# TODO: GET A LIST OF ALL BANNER URLS IN __INIT__
# def get_random_banner_url():
    # return 

@bp.route('/')
@logged_visit
def index():
    db = database_context.get_db()
    # Retrieve recent and featured posts
    recent_posts = db.get_recent_posts(5)
    featured_posts = [db.get_post_by_slug(slug) for slug in fp.get_featured_posts()]
    # Filter out any None values (occurs when a featured post slug is not found in the database)
    featured_posts = [post for post in featured_posts if post]

    # Create dict mapping post_slug -> list of tags
    tags = { 
        post['post_slug']: db.get_tags_by_post_slug(post['post_slug']) \
            for post in recent_posts + featured_posts 
    }
    return render_template(
        'blog/index.html', 
        featured_posts=featured_posts,
        recent_posts=recent_posts, 
        tags=tags,
    )

@bp.route('/posts')
@logged_visit
def posts_page():
    db = database_context.get_db()
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
    db = database_context.get_db()
    # retrieve post data
    post = db.get_post_by_slug(slug)
    if not post:
        abort(404)

    # Alternate possibility to address UTF-8 encoding issues
    html_path = os.path.join(current_app.static_folder, slug, 'post.html')
    with open(html_path, encoding='utf-8', errors='strict') as post_file:
        post_html = render_template_string(post_file.read())

    # retrieve data for the posts before and after
    prev_post = db.get_post_by_postid(post['post_id'] - 1)
    next_post = db.get_post_by_postid(post['post_id'] + 1)

    # retrieve tags this post is tagged under
    tags = db.get_tags_by_post_slug(slug)
    
    return render_template(
        'blog/post.html', 
        post=post, 
        tags=tags,
        post_html=post_html, 
        banner_url=post['post_banner_url'], 
        prev_post=prev_post,
        next_post=next_post,
    )

# show post widgets for all posts under the given tag
@bp.route('/tag/<slug>')
@logged_visit
def tag_view(slug):
    db = database_context.get_db()
    # Make sure the queried tag exists
    if not db.has_tag(slug):
        abort(404)

    tag_title = db.get_tag_by_tagslug(slug)['tag_title']
    # Get list of posts under the given tag    
    posts = db.get_posts_by_tag_slug(slug)
    # # Retrieve tag data for each post
    # tags = { post['post_slug']: db.get_tags_by_post_slug(post['post_slug']) \
    #          for post in posts }
    
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

@bp.route('/changelog')
@logged_visit
def changelog_page():
    return render_template('blog/changelog.html')
    
@bp.errorhandler(404)
@logged_visit
def error_page(error):
    return render_template('blog/404.html'), 404

