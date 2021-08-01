import flask
import datetime
import pathlib
from . import db


# YouTube tutorial for many-to-many relationships: https://www.youtube.com/watch?v=OvhoYbjtiKc
posts_to_tags = db.Table('posts_to_tags',
    db.Column('post', db.Integer, db.ForeignKey('post.id')),
    db.Column('tag', db.Integer, db.ForeignKey('tag.id')),
)


# TODO: WHY AREN'T THE DEFAULTS WORKING?
class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String, nullable=False, unique=True)
    title = db.Column(db.String, nullable=False, default='')
    byline = db.Column(db.String, nullable=False, default='')
    date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now().date())
    tags = db.relationship('Tag', secondary=posts_to_tags, backref=db.backref('posts', lazy='dynamic'))
    is_featured = db.Column(db.Boolean, default=False)

    def get_path(self) -> pathlib.Path:
        """Return Path object to static folder."""
        return pathlib.Path(flask.current_app.static_folder) / self.slug

    def get_image_url(self) -> str:
        return flask.url_for('static', filename=self.slug + '/featured.jpg')

    def get_banner_url(self) -> str:
        return flask.url_for('static', filename=self.slug + '/banner.jpg')

    def get_thumbnail_url(self) -> str:
        return flask.url_for('static', filename=self.slug + '/thumbnail.jpg')

    def __repr__(self):
        return 'Post(title="{}", slug="{}", date={}, tags={})'.format(
            self.title,
            self.slug,
            self.date,
            self.tags,
        )


class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String, nullable=False, unique=True)
    name = db.Column(db.String, nullable=False)
    color = db.Column(db.String, nullable=False)

    def __repr__(self):
        return 'Tag(slug={}, color={})'.format(self.slug, self.color)
