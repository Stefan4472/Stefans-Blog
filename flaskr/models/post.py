import flask
import datetime
import pathlib
from sqlalchemy import asc, desc
from flaskr import db
import flaskr.models.relations as relations



# TODO: WHY AREN'T THE DEFAULTS WORKING?
# TODO: `SLUG` SHOULD REALLY BE THE PRIMARY_KEY
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
    # MD5 hash of the post's HTML
    hash = db.Column(db.String, nullable=False, default='')
    # Tags (Many to Many)
    tags = db.relationship('Tag', secondary=relations.posts_to_tags, backref=db.backref('posts', lazy='dynamic'))
    # Images (One to Many)
    images = db.relationship('PostImage', cascade='all, delete')
    is_featured = db.Column(db.Boolean, default=False)
    is_published = db.Column(db.Boolean, default=False)

    def get_path(self) -> pathlib.Path:
        """Return Path object to static folder."""
        return pathlib.Path(flask.current_app.static_folder) / self.slug

    def get_featured_url(self) -> str:
        return flask.url_for('static', filename=self.slug + '/' + self.featured_filename)

    def get_banner_url(self) -> str:
        return flask.url_for('static', filename=self.slug + '/' + self.banner_filename)

    def get_thumbnail_url(self) -> str:
        return flask.url_for('static', filename=self.slug + '/' + self.thumbnail_filename)

    def find_image(self, filename: str) -> int:
        """Return index of image in this Post with the given filename."""
        for i in range(len(self.images)):
            if self.images[i].filename == filename:
                return i
        return -1

    def load_html(self) -> str:
        """Retrieve the HTML file containing the post's contents and render as template."""
        html_path = self.get_path() / 'post.html'
        with open(html_path, encoding='utf-8', errors='strict') as f:
            return flask.render_template_string(f.read())

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
