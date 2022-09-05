import flask
import werkzeug.exceptions
from sqlalchemy import desc
from flaskr import site_logger
from flaskr.models.post import Post
from flaskr.models.tag import Tag
from flaskr.config import Keys


# Blueprint under which all views will be assigned
BLUEPRINT = flask.Blueprint('blog', __name__)


@BLUEPRINT.route('/')
@site_logger.logged_visit
def index():
    """Site index. Displays featured and recent posts."""
    recent_posts = Post.query\
        .filter(Post.is_published)\
        .order_by(desc(Post.publish_date))\
        .limit(5)\
        .all()
    featured_posts = Post.query\
        .filter(Post.is_featured, Post.is_published)\
        .all()
    return flask.render_template(
        'blog/index.html',
        featured_posts=featured_posts,
        recent_posts=recent_posts,
    )


@BLUEPRINT.route('/posts', defaults={'page': 1})
@BLUEPRINT.route('/posts/<int:page>', methods=['GET'])
@site_logger.logged_visit
def posts_page(page: int = 1):
    """The "posts" page, which displays all posts on the site (paginated)."""
    # Using pagination example from https://stackoverflow.com/a/57348599
    posts = Post.query\
        .filter(Post.is_published)\
        .order_by(desc(Post.publish_date))\
        .paginate(
            page,
            flask.current_app.config[Keys.PAGINATE_POSTS_PER_PAGE],
            error_out=False,
        )
    return flask.render_template(
        'blog/posts.html',
        posts=posts,
    )


@BLUEPRINT.route('/post/<slug>')
@site_logger.logged_visit
def post_view(slug):
    """Shows the page for the post with the specified slug."""
    # Retrieve post
    post = Post.query.filter(Post.slug == slug, Post.is_published).first()
    # Throw 404 if there is no post with the given slug in the database.
    if not post:
        werkzeug.exceptions.abort(404)

    # Note: the post will be rendered via `render_html()` in the template
    return flask.render_template(
        'blog/post.html', 
        post=post, 
        prev_post=post.get_prev(),
        next_post=post.get_next(),
    )


@BLUEPRINT.route('/tag/<slug>')
@site_logger.logged_visit
def tag_view(slug):
    """
    Display all posts that have the given tag.
    TODO: PAGINATION, POTENTIALLY COMBINE INTO THE 'POSTS' URL
    """
    tag = Tag.query.filter(Tag.slug == slug).first()
    # Make sure the queried tag exists
    if not tag:
        werkzeug.exceptions.abort(404)
    return flask.render_template(
        'blog/tag_view.html',
        tag=tag,
        posts=tag.posts.filter(Post.is_published).all(),
    )


@BLUEPRINT.route('/search')
@site_logger.logged_visit
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
            Post.query.filter(Post.slug == result.slug, Post.is_published).first()
            for result in flask.current_app.search_engine.search(query)
        ]

    return flask.render_template(
        'blog/search.html',
        query=query,
        posts=posts,
    )


@BLUEPRINT.route('/portfolio')
@site_logger.logged_visit
def portfolio_page():
    """Show the "Portfolio" page."""
    return flask.render_template('blog/portfolio.html')


@BLUEPRINT.route('/about')
@site_logger.logged_visit
def about_page():
    """Show the "About" page."""
    return flask.render_template('blog/about.html')


@BLUEPRINT.route('/changelog')
@site_logger.logged_visit
def changelog_page():
    """Show the "Changelog" page."""
    return flask.render_template('blog/changelog.html')


@BLUEPRINT.errorhandler(404)
@site_logger.logged_visit
def error_page(error):
    """Show the 404 error page."""
    return flask.render_template('blog/404.html'), 404


@BLUEPRINT.route('/login', methods=['GET'])
def login():
    return flask.render_template('blog/login.html')


@BLUEPRINT.route('/login', methods=['POST'])
def login_auth():
    print(flask.request.form)
    email = flask.request.form.get('email')
    password = flask.request.form.get('password')
    remember = True if flask.request.form.get('remember') else False

    # TODO: on success, go to private page
    return flask.redirect(flask.url_for('blog.login'))


@BLUEPRINT.route('/logout')
def logout():
    return flask.Response(status=200)
