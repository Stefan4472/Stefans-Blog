import os
import functools
import typing
import flask
import werkzeug.exceptions
from sqlalchemy import asc, desc
from . import site_logger
from . import models


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
    recent_posts = models.Post.query.order_by(desc('date')).limit(5).all()
    featured_posts = models.Post.query.filter(models.Post.is_featured).all()
    return flask.render_template(
        'blog/index.html',
        featured_posts=featured_posts,
        recent_posts=recent_posts,
    )


@BLUEPRINT.route('/posts', defaults={'page': 1})
@BLUEPRINT.route('/posts/<int:page>', methods=['GET'])
@logged_visit
def posts_page(page: int = 1):
    """The "posts" page, which displays all posts on the site (paginated)."""
    # Using pagination example from https://stackoverflow.com/a/57348599
    return flask.render_template(
        'blog/posts.html', 
        posts=models.Post.query.paginate(
            page,
            flask.current_app.config['PAGINATE_POSTS_PER_PAGE'],
            error_out=False,
        ),
    )


@BLUEPRINT.route('/post/<slug>')
@logged_visit
def post_view(slug):
    """Shows the page for the post with the specified slug."""
    # Retrieve post
    post = models.Post.query.filter_by(slug=slug).first()
    # Throw 404 if there is no post with the given slug in the database.
    if not post:
        werkzeug.exceptions.abort(404)

    # Retrieve the HTML file containing the post's contents and render as template.
    html_path = os.path.join(flask.current_app.static_folder, slug, 'post.html')
    with open(html_path, encoding='utf-8', errors='strict') as post_file:
        post_html = flask.render_template_string(post_file.read())

    prev_post = models.Post.query.filter(models.Post.date < post.date).order_by(desc('date')).first()
    next_post = models.Post.query.filter(models.Post.date > post.date).order_by(asc('date')).first()

    return flask.render_template(
        'blog/post.html', 
        post=post, 
        post_html=post_html,
        banner_url=post.banner_url,
        prev_post=prev_post,
        next_post=next_post,
    )


@BLUEPRINT.route('/tag/<slug>')
@logged_visit
def tag_view(slug):
    """
    Display all posts that have the given tag.
    TODO: PAGINATION, POTENTIALLY COMBINE INTO THE 'POSTS' URL
    """
    tag = models.Tag.query.filter_by(slug=slug).first()
    # Make sure the queried tag exists
    if not tag:
        werkzeug.exceptions.abort(404)

    return flask.render_template(
        'blog/tag_view.html',
        tag=tag,
        posts=tag.posts.all(),
    )


@BLUEPRINT.route('/search')
@logged_visit
def search_page():
    """
    Displays search results for a particular query, which should be
    passed in as the `query` arg.
    """
    query = flask.request.args.get('query') or ''
    posts = []

    # Perform search and fetch results
    if query:
        posts = [
            models.Post.query.filter_by(slug=result.slug).first()
            for result in flask.current_app.search_engine.search(query)
        ]

    return flask.render_template(
        'blog/search.html',
        query=query,
        posts=posts,
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
