from flaskr import db


class PostImage(db.Model):
    __tablename__ = 'images'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String, nullable=False)
    hash = db.Column(db.String, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    __unique_constraint__ = db.UniqueConstraint('id', 'filename')

    def __repr__(self):
        return 'PostImage(filename="{}", hash="{}", post_id={})'.format(
            self.filename,
            self.hash,
            self.post_id,
        )
