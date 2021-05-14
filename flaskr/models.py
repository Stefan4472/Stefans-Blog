from . import db


# https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#many-to-many
class PostsToTags(db.MetaData):
    post = db.Column(db.Integer, db.ForeignKey('post.id')),
    tag = db.Column(db.Integer, db.ForeignKey('tag.id'))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    byline = db.Column(db.String)
    slug = db.Column(db.String)
    date = db.Column(db.DateTime)
    image_url = db.Column(db.String)
    banner_url = db.Column(db.String)
    thumbnail_url = db.Column(db.String)
    tags = db.RelationshipProperty('Child', secondary=PostsToTags)


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    slug = db.Column(db.String)
    color = db.Column(db.String)
