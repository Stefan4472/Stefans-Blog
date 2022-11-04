import flask
import pathlib
import re
from typing import Optional
from sqlalchemy import asc, desc
from flaskr import db
import flaskr.models.relations as relations
from flaskr.models.file import File
import renderer.markdown
from flaskr.contracts.data_schemas import PostContract


# Regex used to match a HEX color for the `title_color` field
COLOR_REGEX = re.compile('^#[0-9a-fA-F]{6}$')


# TODO: CURRENTLY, MARKDOWN FILES ARE PUBLICLY ACCESSIBLE VIA THE 'STATIC' ROUTE. THIS SHOULD NOT BE THE CASE
# TODO: hash article text?
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
    slug = db.Column(db.String, unique=True, nullable=False, index=True)
    title = db.Column(db.String, nullable=False)
    # Short, engaging description of the post
    byline = db.Column(db.String, nullable=False)
    # Timestamp at which the post was published (if it was published)
    publish_date = db.Column(db.DateTime)

    # Images associated with the post
    featured_id = db.Column(db.Integer, db.ForeignKey('file.id'))
    banner_id = db.Column(db.Integer, db.ForeignKey('file.id'))
    thumbnail_id = db.Column(db.Integer, db.ForeignKey('file.id'))

    # Whether this post is featured
    is_featured = db.Column(db.Boolean, default=False)
    # Whether this post is published
    is_published = db.Column(db.Boolean, default=False)

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

    # TODO: probably refactor this out and just have a `posts` folder
    def get_directory(self) -> pathlib.Path:
        """Return path of this post's directory."""
        return pathlib.Path(flask.current_app.static_folder) / str(self.id)

    def get_markdown_path(self) -> pathlib.Path:
        """Return path of this post's Markdown content."""
        return self.get_directory() / 'post.md'

    def write_content(self, markdown_text: str):
        """Write this post's markdown file. Does not update `last_modified`!"""
        with open(self.get_markdown_path(), 'w+', encoding='utf-8') as out:
            out.write(markdown_text)
        db.session.commit()

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
        return Post.query \
            .filter(Post.publish_date < self.publish_date) \
            .order_by(desc(Post.publish_date)) \
            .first()

    def get_next(self) -> 'Post':
        return Post.query \
            .filter(Post.publish_date > self.publish_date) \
            .order_by(asc(Post.publish_date)) \
            .first()

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
