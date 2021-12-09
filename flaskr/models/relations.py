from flaskr import db


# Track which posts have which tags.
# YouTube tutorial for many-to-many relationships: https://www.youtube.com/watch?v=OvhoYbjtiKc
posts_to_tags = db.Table('posts_to_tags',
    db.Column('post', db.Integer, db.ForeignKey('post.id')),
    db.Column('tag', db.Integer, db.ForeignKey('tag.id')),
)


# Track which posts link which images.
posts_to_images = db.Table('posts_to_images',
    db.Column('post', db.Integer, db.ForeignKey('post.id')),
    db.Column('images2', db.Integer, db.ForeignKey('images2.filename')),
)