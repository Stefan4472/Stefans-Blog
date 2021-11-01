from flaskr import db


class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String, nullable=False, unique=True)
    name = db.Column(db.String, nullable=False)
    color = db.Column(db.String, nullable=False)

    def __repr__(self):
        return 'Tag(slug={}, color={})'.format(self.slug, self.color)
