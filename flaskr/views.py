import os
import functools
import typing
import flask
import werkzeug.exceptions
from . import database_context
from . import site_logger
from . import featured_posts as fp
from . import models
from .database import db


# Blueprint under which all views will be assigned
BLUEPRINT = flask.Blueprint('blog', __name__)


def logged_visit(f: typing.Callable):
    """Decorator that logs the url being accessed. Simply calls `log_visit()`."""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        site_logger.log_visit()
        return f(*args, **kwargs)
    return decorated_function


@BLUEPRINT.route('/')
@logged_visit
def index():
    """Site index. Displays featured and recent posts."""
    post = models.Post.query.get(1)
    print(post)
    # t = models.Tag(slug='yo', name='hi')
    # print(tag)
    # print(t)
    # db.create_all()
    # db.session.add(t)
    # db.session.commit()

    # db = database_context.get_db()
    # # Retrieve recent and featured posts
    # # TODO: MOVE FEATURED POSTS TO THE DATABASE
    # recent_posts = db.get_recent_posts(5)
    # featured_posts = \
    #     [db.get_post_by_slug(slug) for slug in fp.get_featured_posts()]
    #
    # # Filter out any `None` values.
    # # This occurs when a featured post slug is not found in the database,
    # # and should generally be an exceptional case (i.e., the user made a
    # # mistake in th e"featured_posts" file.
    # featured_posts = [post for post in featured_posts if post]
    #
    # # Create dict mapping post_slug -> list of tags
    # # TODO: IMPROVE THE WAY WE HANDLE TAGS (CONFUSING)
    # tags = {
    #     post['post_slug']: db.get_tags_by_post_slug(post['post_slug']) \
    #         for post in recent_posts + featured_posts
    # }
    #
    # return flask.render_template(
    #     'blog/index.html',
    #     featured_posts=featured_posts,
    #     recent_posts=recent_posts,
    #     tags=tags,
    # )
    return 'hello world'


@BLUEPRINT.route('/posts')
@logged_visit
def posts_page():
    """
    The "posts" page, which displays all posts on the site.
    Also handles the user entering a search query.

    TODO: PAGINATION, ALLOW FILTERING BY TAGS, AND FIND A BETTER WAY TO
    HANDLE SEARCH QUERIES
    """
    db = database_context.get_db()
    # Retrieve search query (may be None)
    query = flask.request.args.get('query')

    # Perform the search and retrieve results if user has entered a query
    if query:
        search_results = flask.current_app.search_engine.search(query)
        posts = [db.get_post_by_slug(result.slug) for result in search_results]
    # Otherwise, get all posts
    else:
        posts = db.get_all_posts()

    # Retrieve tag data
    tags = {
        post['post_slug']: db.get_tags_by_post_slug(post['post_slug']) \
            for post in posts
    }

    # Render and return
    return flask.render_template(
        'blog/posts.html', 
        search_query=query, 
        posts=posts, 
        tags=tags,
    )


@BLUEPRINT.route('/post/<slug>')
@logged_visit
def post_view(slug):
    """Shows the page for the post with the specified slug."""
    db = database_context.get_db()
    # Retrieve post data
    post = db.get_post_by_slug(slug)
    # Throw 404 if there is no post with the given slug in the database.
    if not post:
        werkzeug.exceptions.abort(404)

    # Retrieve the HTML file containing the post's contents,
    # and render it as a template.
    html_path = os.path.join(flask.current_app.static_folder, slug, 'post.html')
    with open(html_path, encoding='utf-8', errors='strict') as post_file:
        post_html = flask.render_template_string(post_file.read())

    # Retrieve data for the posts coming before and after the current post.
    # TODO: GET NEXT/PREV BY *CHRONOLOGICAL* ORDER
    prev_post = db.get_post_by_postid(post['post_id'] - 1)
    next_post = db.get_post_by_postid(post['post_id'] + 1)

    # Retrieve tag info for this post
    tags = db.get_tags_by_post_slug(slug)
    
    return flask.render_template(
        'blog/post.html', 
        post=post, 
        tags=tags,
        post_html=post_html, 
        banner_url=post['post_banner_url'], 
        prev_post=prev_post,
        next_post=next_post,
    )


@BLUEPRINT.route('/tag/<slug>')
@logged_visit
def tag_view(slug):
    """Display all posts that have the given tag.
    TODO: PAGINATION, POTENTIALLY COMBINE INTO THE 'POSTS' URL
    """
    db = database_context.get_db()
    # Make sure the queried tag exists
    if not db.has_tag(slug):
        werkzeug.exceptions.abort(404)

    tag_title = db.get_tag_by_tagslug(slug)['tag_title']
    # Get list of posts under the given tag    
    posts = db.get_posts_by_tag_slug(slug)
    # # Retrieve tag data for each post
    # tags = { post['post_slug']: db.get_tags_by_post_slug(post['post_slug']) \
    #          for post in posts }
    
    return flask.render_template(
        'blog/tag_view.html', 
        posts=posts,
        tag_title=tag_title,
    )


@BLUEPRINT.route('/portfolio')
@logged_visit
def portfolio_page():
    """Show the "Portfolio" page."""
    return flask.render_template('blog/portfolio.html')


@BLUEPRINT.route('/about')
@logged_visit
def about_page():
    """Show the "About" page."""
    return flask.render_template('blog/about.html')


@BLUEPRINT.route('/changelog')
@logged_visit
def changelog_page():
    """Show the "Changelog" page."""
    return flask.render_template('blog/changelog.html')


@BLUEPRINT.errorhandler(404)
@logged_visit
def error_page(error):
    """Show the 404 error page."""
    return flask.render_template('blog/404.html'), 404
