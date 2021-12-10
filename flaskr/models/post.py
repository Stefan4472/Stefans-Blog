import flask
import datetime
import pathlib
import re
from sqlalchemy import asc, desc
from flaskr import db
import flaskr.models.relations as relations
from flaskr.models.image import Image
import renderer.markdown as md2


# Regex used to match a HEX color for the `title_color` field
COLOR_REGEX = re.compile('^#[0-9a-fA-F]{6}$')


# TODO: WHY AREN'T THE DEFAULTS WORKING?
# TODO: `SLUG` SHOULD REALLY BE THE PRIMARY_KEY
# TODO: CURRENTLY, MARKDOWN FILES ARE PUBLICLY ACCESSIBLE VIA THE 'STATIC' ROUTE. THIS SHOULD NOT BE THE CASE
class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String, nullable=False, unique=True)
    title = db.Column(db.String, nullable=False, default='')
    byline = db.Column(db.String, nullable=False, default='')
    date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now().date())
    # Image filenames
    featured_filename = db.Column(db.String, nullable=False, default='')
    banner_filename = db.Column(db.String, nullable=False, default='')
    thumbnail_filename = db.Column(db.String, nullable=False, default='')
    # MD5 hash of the post's Markdown
    hash = db.Column(db.String, nullable=False, default='')
    is_featured = db.Column(db.Boolean, default=False)
    is_published = db.Column(db.Boolean, default=False)
    # TODO: ADD `CHECK` CONSTRAINT TO ENSURE VALID HEX COLOR.
    #   This is unfortunately difficult to do without a full database migration...
    #   leaving for another day.
    title_color = db.Column(db.String(length=7), server_default='#FFFFFF')

    # Tags (Many to Many)
    tags = db.relationship(
        'Tag',
        secondary=relations.posts_to_tags,
        backref=db.backref('posts', lazy='dynamic'),
    )
    # Images (Many to Many)
    images = db.relationship(
        'Image',
        secondary=relations.posts_to_images,
        backref=db.backref('posts', lazy='dynamic'),
    )

    # TODO: MAKE INTO ATTRIBUTES
    def get_directory(self) -> pathlib.Path:
        """Return Path object to static folder."""
        return pathlib.Path(flask.current_app.static_folder) / self.slug

    def get_featured_url(self) -> str:
        return flask.url_for('static', filename=self.featured_filename)

    def get_banner_url(self) -> str:
        return flask.url_for('static', filename=self.banner_filename)

    def get_thumbnail_url(self) -> str:
        return flask.url_for('static', filename=self.thumbnail_filename)

    def get_markdown_path(self) -> pathlib.Path:
        return self.get_directory() / 'post.md'

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

    def __repr__(self):
        return 'Post(title="{}", slug="{}", date={}, tags={})'.format(
            self.title,
            self.slug,
            self.date,
            self.tags,
        )
