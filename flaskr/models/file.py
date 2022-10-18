from enum import Enum
from flaskr import db


class FileType(Enum):
    """General file types used to classify uploaded files."""
    Image = 'IMAGE'
    Video = 'VIDEO'
    Document = 'DOCUMENT'


class File(db.Model):
    """Represents a file uploaded to the server."""
    __tablename__ = 'file'
    # UUID
    id = db.Column(db.String, primary_key=True)
    # User-given name at time of upload
    upload_name = db.Column(db.String, nullable=False)
    # Timestamp of upload
    upload_date = db.Column(db.DateTime, nullable=False)
    # ID of the user who uploaded this file (one-to-many)
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # The user who uploaded this file (one-to-many)
    # See https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#one-to-many
    uploaded_by = db.relationship('User', back_populates='files')
    # File type
    filetype = db.Column(db.Enum(FileType), nullable=False)
    # Name of the file as it is stored on the system
    filename = db.Column(db.String, unique=True, nullable=False)
    # Size of the file, in bytes
    size = db.Column(db.Integer, nullable=False)
    # MD5 hash of the file contents
    hash = db.Column(db.String, unique=True, nullable=False)
