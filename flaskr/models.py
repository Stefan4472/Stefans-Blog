from . import db
# TODO: LOOK INTO SETTING THE 'LAZY' FIELD FOR BETTER PERFORMANCE


# https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#many-to-many
posts_to_tags = db.Table('posts_to_tags',
    db.Column('post', db.Integer, db.ForeignKey('post.id')),
    db.Column('tag', db.Integer, db.ForeignKey('tag.id')),
)


class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String, nullable=False, unique=True)
    title = db.Column(db.String, nullable=False)
    byline = db.Column(db.String, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    # TODO: THESE URLS CAN BE STATICALLY DETERMINED FROM OTHER INFO
    image_url = db.Column(db.String, nullable=False)
    banner_url = db.Column(db.String, nullable=False)
    thumbnail_url = db.Column(db.String, nullable=False)
    tags = db.relationship('Tag', secondary=posts_to_tags)
    is_featured = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return 'Post(slug={}, tags={})'.format(self.slug, self.tags)


class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String, nullable=False, unique=True)
    name = db.Column(db.String, nullable=False)
    color = db.Column(db.String, nullable=False)

    def __repr__(self):
        return 'Tag(slug={}, color={})'.format(self.slug, self.color)
