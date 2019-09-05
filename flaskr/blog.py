from flask import (
    Blueprint, flash, g, redirect, render_template, render_template_string,
    request, url_for, current_app
)
from werkzeug.exceptions import abort
from flaskr.database import get_db
from flaskr.site_logger import log_visit
import os
import flaskr.featured_posts as fp
from flaskr.search_engine.index import restore_index_from_file

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    log_visit()  # TODO: ANY WAY TO CALL log_visit BY DEFAULT?
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
def posts_page():
    log_visit()
    db = get_db()
    posts = db.get_all_posts()
    tags = { post['post_slug']: db.get_tags_by_post_slug(post['post_slug']) \
             for post in posts }
    return render_template('blog/posts.html', posts=posts, tags=tags)

@bp.route('/post/<slug>')
def post_view(slug):
    log_visit()
    print ('Looking up {}'.format(slug))
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
def tag_view(slug):
    log_visit()
    db = get_db()
    if not db.has_tag(slug):
        abort(404)
    tag_title = db.get_tag_by_tagslug(slug)['tag_title']
    posts = db.get_posts_by_tag_slug(slug)
    return render_template('blog/tag_view.html', posts=posts, \
        tag_title=tag_title)

@bp.route('/portfolio')
def portfolio_page():
    log_visit()
    return render_template('blog/portfolio.html')

@bp.route('/about')
def about_page():
    log_visit()
    return render_template('blog/about.html')

@bp.route('/highlights')
def highlights_page():
    log_visit()
    return render_template('blog/highlights.html')

@bp.route('/search')
def search_page():
    log_visit()
    query = request.args.get('query')
    #if search_engine is None:
    #    search_engine = index.restore_index_from_file(current_app.config['SEARCH_INDEX_FILE'])
    # TODO: NEED A PERSISTENT INDEX OBJECT!
    search_engine = restore_index_from_file(current_app.config['SEARCH_INDEX_FILE'])
    search_result = search_engine.search(query)
    return '{}: \n{}'.format(query, search_result)

@bp.errorhandler(404)
def error_page(error):
    log_visit()
    return render_template('blog/404.html'), 404
