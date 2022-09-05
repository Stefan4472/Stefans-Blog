from flask_login import UserMixin
from flaskr import db


class User(db.Model, UserMixin):
    """A registered user of the website."""
    id = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    # Password hash
    password = db.Column(db.String(100))
    # Full name (human readable)
    name = db.Column(db.String(30))
