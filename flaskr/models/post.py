import flask
import datetime as dt
import pathlib
import re
import hashlib
import shutil
from typing import Optional
from sqlalchemy import asc, desc
from flaskr import db
import flaskr.models.relations as relations
from flaskr.models.image import Image
from flaskr.models.file import File
from flaskr.models.tag import Tag
from flaskr.models.user import User
import flaskr.api.constants as constants
import renderer.markdown
from flaskr.contracts.data_schemas import PostContract


# Regex used to match a HEX color for the `title_color` field
COLOR_REGEX = re.compile('^#[0-9a-fA-F]{6}$')


# TODO: CURRENTLY, MARKDOWN FILES ARE PUBLICLY ACCESSIBLE VIA THE 'STATIC' ROUTE. THIS SHOULD NOT BE THE CASE
class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    # ID of the user who created this post
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # The user who created this post
    author = db.relationship('User', back_populates='posts')
    # Timestamp at which the post was last modified
    last_modified = db.Column(db.DateTime, nullable=False)
    # "slug" used to create a URL for this post
    slug = db.Column(db.String, unique=True)
    title = db.Column(db.String, unique=True)
    # Short, engaging description of the post
    byline = db.Column(db.String)
    # Timestamp at which the post was published (if it was published)
    publish_date = db.Column(db.DateTime)

    # Images associated with the post
    featured_id = db.Column(db.Integer, db.ForeignKey('file.id'))
    banner_id = db.Column(db.Integer, db.ForeignKey('file.id'))
    thumbnail_id = db.Column(db.Integer, db.ForeignKey('file.id'))

    # Whether this post is featured
    is_featured = db.Column(db.Boolean)
    # Whether this post is published
    is_published = db.Column(db.Boolean)

    # Tags associated with this post (Many to Many)
    tags = db.relationship(
        'Tag',
        secondary=relations.posts_to_tags,
        # Note: this backref allows us to call Tag.posts on a `Tag` instance
        backref=db.backref('posts', lazy='dynamic'),
    )
    # Images (Many to Many)  TODO: file references
    # images = db.relationship(
    #     'Image',
    #     secondary=relations.posts_to_images,
    #     # Note: this backref allows us to call Image.posts on an `Image` instance
    #     backref=db.backref('images', lazy='dynamic'),
    # )

    @property
    def featured_image(self) -> Optional[File]:
        return File.query.filter_by(id=self.featured_id).first()

    @property
    def banner_image(self) -> Optional[File]:
        return File.query.filter_by(id=self.banner_id).first()

    @property
    def thumbnail_image(self) -> Optional[File]:
        return File.query.filter_by(id=self.thumbnail_id).first()

    def make_contract(self) -> PostContract:
        return PostContract(
            id=self.id,
            author=self.author.make_contract(),
            last_modified=self.last_modified,
            is_featured=self.is_featured,
            is_published=self.is_published,
            slug=self.slug,
            title=self.title,
            byline=self.byline,
            publish_date=self.publish_date,
            featured_image=self.featured_image if self.featured_id else None,
            banner_image=self.banner_image if self.banner_id else None,
            thumbnail_image=self.thumbnail_image if self.thumbnail_id else None,
            tags=[t.make_contract() for t in self.tags],
        )


    '''
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
        self.publish_date = publish_date if publish_date else dt.datetime.now()
        self.is_featured = is_featured if is_featured is not None else False
        self.is_published = is_published if is_published is not None else False
        self.set_title_color(title_color if title_color else '#FFFFFF')
        self.tags = tags if tags else []
        self.set_markdown(markdown_text if markdown_text else '')

    def get_directory(self) -> pathlib.Path:
        """Return Path object to static folder."""
        return pathlib.Path(flask.current_app.static_folder) / self.slug

    def get_featured_image(self) -> Image:
        return Image.query.filter_by(id=self.featured_id).first()

    def get_banner_image(self) -> Image:
        return Image.query.filter_by(id=self.banner_id).first()

    def get_thumbnail_image(self) -> Image:
        return Image.query.filter_by(id=self.thumbnail_id).first()

    def get_markdown_path(self) -> pathlib.Path:
        return self.get_directory() / 'post.md'

    def set_featured_image(self, image: Image):
        if (image.width, image.height) != constants.FEATURED_IMG_SIZE:
            raise ValueError('Featured image has the wrong dimensions')
        if self.featured_id:
            curr_featured = Image.query.filter_by(id=self.featured_id).first()
            self.images.remove(curr_featured)
        self.featured_id = image.id
        if image not in self.images:
            self.images.append(image)

    def set_banner_image(self, image: Image):
        if (image.width, image.height) != constants.BANNER_SIZE:
            raise ValueError('Banner image has the wrong dimensions')
        if self.banner_id:
            curr_banner = Image.query.filter_by(id=self.banner_id).first()
            self.images.remove(curr_banner)
        self.banner_id = image.id
        if image not in self.images:
            self.images.append(image)

    def set_thumbnail_image(self, image: Image):
        if (image.width, image.height) != constants.THUMBNAIL_SIZE:
            raise ValueError('Thumbnail image has the wrong dimensions')
        if self.thumbnail_id:
            curr_thumbnail = Image.query.filter_by(id=self.thumbnail_id).first()
            self.images.remove(curr_thumbnail)
        self.thumbnail_id = image.id
        if image not in self.images:
            self.images.append(image)

    # TODO: honestly, the image stuff needs some real testing
    def set_markdown(self, markdown_text: str):
        # Remove all images except for featured, banner, and thumbnail
        self.images = [
            img for img in self.images if
            img.id == self.featured_id
            or img.id == self.banner_id
            or img.id == self.thumbnail_id]
        # Look up images referenced in the Markdown and ensure they exist
        for image_name in renderer.markdown.find_images(markdown_text):
            found_image = Image.query.filter_by(filename=image_name).first()
            if found_image:
                self.images.append(found_image)
            else:
                msg = f'Image file not found on server: {image_name}'
                raise ValueError(msg)

        # Render HTML to check for errors
        try:
            renderer.markdown.render_string(markdown_text)
        except Exception as e:
            raise ValueError(f'Error processing Markdown: {e}')

        # Create directory
        # TODO: probably refactor this out and just have a `posts` folder
        self.get_directory().mkdir(exist_ok=True)
        with open(self.get_markdown_path(), 'w+', encoding='utf-8') as out:
            out.write(markdown_text)
        self.hash = hashlib.md5(bytes(markdown_text, encoding='utf8')).hexdigest()

        # Add Markdown file to the search engine index
        flask.current_app.search_engine.index_string(
            markdown_text, self.slug, allow_overwrite=True)
        flask.current_app.search_engine.commit()

    def render_html(self) -> str:
        """Retrieve the Markdown file containing the post's contents and render to HTML."""
        with open(self.get_markdown_path(), encoding='utf-8', errors='strict') as f:
            markdown = f.read()  # TODO: this is very inefficient. Fix!
            # Resolve image URLs
            for image_name in renderer.markdown.find_images(markdown):
                found_image = Image.query.filter_by(filename=image_name).first()
                markdown = markdown.replace(image_name, found_image.get_url())
            html = renderer.markdown.render_string(markdown)

            # Render as a template to allow expanding `url_for()` calls (for example)
            return flask.render_template_string(html)

    def get_prev(self) -> 'Post':
        return Post.query\
            .filter(Post.publish_date < self.publish_date)\
            .order_by(desc(Post.publish_date))\
            .first()

    def get_next(self) -> 'Post':
        return Post.query\
            .filter(Post.publish_date > self.publish_date)\
            .order_by(asc(Post.publish_date))\
            .first()

    def to_dict(self) -> dict:
        return {
            constants.KEY_SLUG: self.slug,
            constants.KEY_TITLE: self.title,
            constants.KEY_BYLINE: self.byline,
            constants.KEY_DATE: self.publish_date.strftime(constants.DATE_FORMAT),
            constants.KEY_IMAGE: self.featured_id,
            constants.KEY_BANNER: self.banner_id,
            constants.KEY_THUMBNAIL: self.thumbnail_id,
            constants.KEY_HASH: self.hash,
            constants.KEY_TAGS: [tag.slug for tag in self.tags],
            constants.KEY_IMAGES: {
                image.id: {'hash': image.hash} for image in self.images
            },
            constants.KEY_FEATURE: self.is_featured,
            constants.KEY_PUBLISH: self.is_published,
        }

    def run_delete_logic(self):
        """
        Perform logic to delete the post. The actual database record must
        then be deleted via SQLAlchemy.
        """
        shutil.rmtree(self.get_directory())
        flask.current_app.search_engine.remove_document(self.slug)

    def __repr__(self):
        return 'Post(title="{}", slug="{}", date={}, tags={})'.format(
            self.title,
            self.slug,
            self.publish_date,
            self.tags,
        )
    '''
