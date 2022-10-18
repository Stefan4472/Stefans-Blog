from flask_login import UserMixin
from flaskr import db
from flaskr.contracts.data_schemas import UserContract


class User(db.Model, UserMixin):
    """A registered user of the website."""
    __tablename__ = 'user'
    # Unique ID
    id = db.Column(db.Integer, primary_key=True)
    # User's email address
    email = db.Column(db.String(100), unique=True)
    # User's *hashed* password
    password = db.Column(db.String(100))
    # User's full name (human readable) used for display purposes
    name = db.Column(db.String(30))
    # Files uploaded by this user
    # TODO: check whether this will cause performance problems.
    files = db.relationship('File', back_populates='uploaded_by')

    def make_contract(self) -> UserContract:
        return UserContract(
            id=self.id,
            name=self.name,
        )
