import flask
import datetime as dt
import pathlib
import re
import hashlib
import typing
from sqlalchemy import asc, desc
from flaskr import db
import flaskr.models.relations as relations
from flaskr.models.image import Image
from flaskr.models.tag import Tag
import flaskr.api.constants as constants
import renderer.markdown as md2


# Regex used to match a HEX color for the `title_color` field
COLOR_REGEX = re.compile('^#[0-9a-fA-F]{6}$')


# TODO: CURRENTLY, MARKDOWN FILES ARE PUBLICLY ACCESSIBLE VIA THE 'STATIC' ROUTE. THIS SHOULD NOT BE THE CASE
class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String, unique=True, nullable=False)
    title = db.Column(db.String, nullable=False)
    byline = db.Column(db.String, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    # Image filenames TODO: change to image ID
    featured_filename = db.Column(db.String, nullable=False)
    banner_filename = db.Column(db.String, nullable=False)
    thumbnail_filename = db.Column(db.String, nullable=False)
    # MD5 hash of the post's Markdown
    hash = db.Column(db.String, nullable=False)
    is_featured = db.Column(db.Boolean, nullable=False)
    is_published = db.Column(db.Boolean, nullable=False)
    # Note: checking for valid hex colors is left to the application
    title_color = db.Column(db.String(length=7), nullable=False)

    # Tags (Many to Many)
    tags = db.relationship(
        'Tag',
        secondary=relations.posts_to_tags,
        # Note: this backref allows us to call Tag.posts on a `Tag` instance
        backref=db.backref('posts', lazy='dynamic'),
    )
    # Images (Many to Many)
    images = db.relationship(
        'Image',
        secondary=relations.posts_to_images,
        # Note: this backref allows us to call Image.posts on an `Image` instance
        backref=db.backref('images', lazy='dynamic'),
    )

    def __init__(
            self,
            slug: str,
            title: str,
            featured_image: 'Image',
            banner_image: 'Image',
            thumbnail_image: 'Image',
            byline: str = None,
            publish_date: dt.datetime = None,
            is_featured: bool = None,
            is_published: bool = None,
            title_color: str = None,
            tags: typing.List[Tag] = None,
            markdown_text: str = None,
    ):
        self.slug = slug
        self.title = title
        self.set_featured_image(featured_image)
        self.set_banner_image(banner_image)
        self.set_thumbnail_image(thumbnail_image)
        self.byline = byline if byline else ''
        self.date = publish_date if publish_date else dt.datetime.now()
        self.is_featured = is_featured if is_featured is not None else False
        self.is_published = is_published if is_published is not None else False
        self.set_title_color(title_color if title_color else '#FFFFFF')
        self.tags = tags if tags else []
        self.set_markdown(markdown_text if markdown_text else '')

    # TODO: MAKE INTO ATTRIBUTES
    def get_directory(self) -> pathlib.Path:
        """Return Path object to static folder."""
        return pathlib.Path(flask.current_app.static_folder) / self.slug

    # TODO: refactor to `get_featured_image()`
    def get_featured_url(self) -> str:
        return flask.url_for('static', filename=self.featured_filename)

    def get_banner_url(self) -> str:
        return flask.url_for('static', filename=self.banner_filename)

    def get_thumbnail_url(self) -> str:
        return flask.url_for('static', filename=self.thumbnail_filename)

    def get_markdown_path(self) -> pathlib.Path:
        return self.get_directory() / 'post.md'

    def set_featured_image(self, image: Image):
        if (image.width, image.height) != constants.FEATURED_IMG_SIZE:
            raise ValueError('Featured image has the wrong dimensions')
        if self.featured_filename:
            curr_featured = \
                Image.query.filter_by(filename=self.featured_filename).first()
            self.images.remove(curr_featured)
        self.featured_filename = image.filename
        if image not in self.images:
            self.images.append(image)

    def set_banner_image(self, image: Image):
        if (image.width, image.height) != constants.BANNER_SIZE:
            raise ValueError('Banner image has the wrong dimensions')
        if self.banner_filename:
            curr_banner = \
                Image.query.filter_by(filename=self.banner_filename).first()
            self.images.remove(curr_banner)
        self.banner_filename = image.filename
        if image not in self.images:
            self.images.append(image)

    def set_thumbnail_image(self, image: Image):
        if (image.width, image.height) != constants.THUMBNAIL_SIZE:
            raise ValueError('Thumbnail image has the wrong dimensions')
        if self.thumbnail_filename:
            curr_thumbnail = \
                Image.query.filter_by(filename=self.thumbnail_filename).first()
            self.images.remove(curr_thumbnail)
        self.thumbnail_filename = image.filename
        if image not in self.images:
            self.images.append(image)

    def set_title_color(self, color: str):
        if not re.compile(constants.COLOR_REGEX).match(color):
            raise ValueError('Improper HEX color (expects #[A-F]{6})')
        self.title_color = color

    def set_markdown(self, markdown_text: str):
        # Create directory
        # TODO: probably refactor this out and just have a `posts` folder
        self.get_directory().mkdir(exist_ok=True)
        with open(self.get_markdown_path(), 'w+', encoding='utf-8') as out:
            out.write(markdown_text)
        self.hash = hashlib.md5(bytes(markdown_text, encoding='utf8')).hexdigest()

    def render_html(self) -> str:
        """Retrieve the Markdown file containing the post's contents and render to HTML."""
        with open(self.get_markdown_path(), encoding='utf-8', errors='strict') as f:
            markdown = f.read()
            # Resolve image URLs. TODO: THIS IS REALLY INEFFICIENT. COULD ALSO ITERATE OVER THE POST'S IMAGES
            for image_name in md2.find_images(markdown):
                found_image = Image.query.filter_by(filename=image_name).first()
                markdown = md2.replace_image(markdown, image_name, found_image.get_url())
            html = md2.render_string(markdown)

            # Render as a template to allow expanding `url_for()` calls (for example)
            return flask.render_template_string(html)

    def get_prev(self) -> 'Post':
        return Post.query\
            .filter(Post.date < self.date)\
            .order_by(desc('date'))\
            .first()

    def get_next(self) -> 'Post':
        return Post.query\
            .filter(Post.date > self.date)\
            .order_by(asc('date'))\
            .first()

    def to_dict(self) -> dict:
        return {
            constants.KEY_SLUG: self.slug,
            constants.KEY_TITLE: self.title,
            constants.KEY_BYLINE: self.byline,
            constants.KEY_DATE: self.date.strftime(constants.DATE_FORMAT),
            constants.KEY_IMAGE: self.featured_filename,
            constants.KEY_BANNER: self.banner_filename,
            constants.KEY_THUMBNAIL: self.thumbnail_filename,
            constants.KEY_HASH: self.hash,
            constants.KEY_TAGS: [tag.slug for tag in self.tags],
            constants.KEY_IMAGES: {
                image.filename: {'hash': image.hash} for image in self.images
            },
            constants.KEY_FEATURE: self.is_featured,
            constants.KEY_PUBLISH: self.is_published,
        }

    def __repr__(self):
        return 'Post(title="{}", slug="{}", date={}, tags={})'.format(
            self.title,
            self.slug,
            self.date,
            self.tags,
        )
