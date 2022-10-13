from typing import Dict
from flaskr import db


class Tag(db.Model):
    __tablename__ = 'tag'
    slug = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    # Note: checking for valid hex colors is left to the application
    color = db.Column(db.String, nullable=False)

    def __repr__(self):
        return 'Tag(slug={}, color={})'.format(self.slug, self.color)

    # TODO: a better way to do serialization
    def to_json(self) -> Dict:
        return {
            'slug': self.slug,
            'name': self.name,
            'description': self.description,
            'color': self.color,
        }
