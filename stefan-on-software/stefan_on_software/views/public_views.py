import flask
import werkzeug.exceptions
from flask_login import current_user, login_user
from sqlalchemy import desc
from stefan_on_software import site_logger
from stefan_on_software.auth import verify_login
from stefan_on_software.models.post import Post
from stefan_on_software.models.tag import Tag
from stefan_on_software.site_config import ConfigKeys
from stefan_on_software.views.page_metadata import PageMetadata

# Blueprint under which all views will be assigned
BLUEPRINT = flask.Blueprint("blog", __name__)


def make_default_metadata(title: str, description: str) -> PageMetadata:
    return PageMetadata(
        title,
        description,
        "Stefan Kussmaul",
        # TODO: separate default banner for large screen vs. small
        flask.url_for("static", filename="site-banner.jpg", _external=True),
        flask.url_for("static", filename="site-banner.jpg", _external=True),
    )


@BLUEPRINT.route("/")
@site_logger.logged_visit
def index():
    """Site index. Displays featured and recent posts."""
    recent_posts = (
        Post.query.filter(Post.is_published)
        .order_by(desc(Post.publish_date))
        .limit(5)
        .all()
    )
    featured_posts = Post.query.filter(Post.is_featured, Post.is_published).all()
    return flask.render_template(
        "blog/index.html",
        featured_posts=featured_posts,
        recent_posts=recent_posts,
        page_meta=make_default_metadata(
            "Home",
            "Stefan Kussmaul's personal blog about software, data analysis, and life in general.",
        ),
    )


@BLUEPRINT.route("/posts", defaults={"page": 1})
@BLUEPRINT.route("/posts/<int:page>", methods=["GET"])
@site_logger.logged_visit
def posts_page(page: int = 1):
    """The "posts" page, which displays all posts on the site (paginated)."""
    # Using pagination example from https://stackoverflow.com/a/57348599
    posts = (
        Post.query.filter(Post.is_published)
        .order_by(desc(Post.publish_date))
        .paginate(
            page=page,
            per_page=flask.current_app.config[ConfigKeys.PAGINATE_POSTS_PER_PAGE],
            error_out=False,
        )
    )
    return flask.render_template(
        "blog/posts.html",
        posts=posts,
        page_meta=make_default_metadata(
            f"Posts (page {page})", "Posts published on StefanOnSoftware."
        ),
    )


@BLUEPRINT.route("/post/<slug>")
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
        "blog/post.html",
        post=post,
        prev_post=post.get_prev(),
        next_post=post.get_next(),
        page_meta=PageMetadata(
            post.title,
            post.byline,
            post.author.name,
            post.banner_image.make_url(),
            post.featured_image.make_url(),
        ),
    )


@BLUEPRINT.route("/tag/<slug>")
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
        "blog/tag_view.html",
        tag=tag,
        posts=tag.posts.filter(Post.is_published).all(),
        page_meta=make_default_metadata(
            tag.name, f"Posts tagged under {tag.name}: {tag.description}"
        ),
    )


@BLUEPRINT.route("/search")
@site_logger.logged_visit
def search_page():
    """
    Displays search results for a particular query, which should be
    passed in as the `query` arg.
    """
    query = flask.request.args.get("query") or ""
    posts = []

    # Run the query, which will return a list of PostIds. Retrieve them from the database.
    # TODO: would be great to have a way to unit test this. Possibly merge into the '/posts' page?
    if query:
        posts = [
            Post.query.filter(Post.id == int(result.slug), Post.is_published).first()
            for result in flask.current_app.search_engine.search(query)
        ]

    return flask.render_template(
        "blog/search.html",
        query=query,
        posts=posts,
        page_meta=make_default_metadata(
            f"Search Results for '{query}'",
            "Displaying search results for StefanOnSoftware",
        ),
    )


@BLUEPRINT.route("/portfolio")
@site_logger.logged_visit
def portfolio_page():
    """Show the "Portfolio" page."""
    return flask.render_template(
        "blog/portfolio.html",
        page_meta=make_default_metadata(
            "Portfolio", "A selection of personal projects created by Stefan."
        ),
    )


@BLUEPRINT.route("/about")
@site_logger.logged_visit
def about_page():
    """Show the "About" page."""
    return flask.render_template(
        "blog/about.html",
        page_meta=make_default_metadata("About", "All you need to know about Stefan"),
    )


@BLUEPRINT.errorhandler(404)
@site_logger.logged_visit
def error_page(error):
    """Show the 404 error page."""
    return (
        flask.render_template(
            "blog/404.html",
            page_meta=make_default_metadata(
                "404 Error", "The page you are trying to access does not exist"
            ),
        ),
        404,
    )


@BLUEPRINT.route("/login", methods=["GET"])
def login():
    if current_user.is_authenticated:
        return flask.redirect(flask.url_for("internal.landing"))
    # Don't allow search engines to crawl this page.
    meta = make_default_metadata("Login", "Login to the website.")
    meta.allow_indexing = False
    return flask.render_template(
        "blog/login.html",
        page_meta=meta,
    )


@BLUEPRINT.route("/sitemap.xml", methods=["GET"])
def sitemap():
    # As advised by https://stackoverflow.com/a/14625619, the sitemap file
    # should be stored in 'static' but be served via its own route.
    return flask.send_file(flask.current_app.config[ConfigKeys.SITEMAP_PATH])


@BLUEPRINT.route("/login", methods=["POST"])
def login_auth():
    email = flask.request.form.get("email")
    password = flask.request.form.get("password")
    remember = bool(flask.request.form.get("remember"))

    try:
        user = verify_login(email, password)
    except ValueError:
        # Error: reload the login page
        return flask.redirect(flask.url_for("blog.login"))

    # Success: login and redirect to internal page
    login_user(user, remember=remember)
    flask.current_app.logger.debug(f"User {email} logged in")
    return flask.redirect(flask.url_for("internal.landing"))
