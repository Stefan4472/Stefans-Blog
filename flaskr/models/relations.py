from flaskr import db


# Many-to-many table storing Post<->Tags
# YouTube tutorial for many-to-many relationships: https://www.youtube.com/watch?v=OvhoYbjtiKc
posts_to_tags = db.Table(
    'posts_to_tags',
    db.Column('post', db.Integer, db.ForeignKey('post.id')),
    db.Column('tag', db.Integer, db.ForeignKey('tag.slug')),
)


# Many-to-many table storing Post<->Image.
posts_to_images = db.Table(
    'posts_to_images',
    db.Column('post', db.Integer, db.ForeignKey('post.id')),
    db.Column('image', db.Integer, db.ForeignKey('image.id')),
)
