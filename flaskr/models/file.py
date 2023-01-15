from enum import Enum
from pathlib import Path

from flask import current_app, url_for

from flaskr import db
from flaskr.contracts.data_schemas import FileContract, UserContract


class FileType(Enum):
    """General file types used to classify uploaded files."""

    Image = "IMAGE"
    # Video = 'VIDEO'
    Document = "DOCUMENT"


class File(db.Model):
    """Represents a file uploaded to the server."""

    __tablename__ = "file"
    # UUID
    id = db.Column(db.String, primary_key=True)
    # User-given name at time of upload
    upload_name = db.Column(db.String, nullable=False)
    # Timestamp of upload
    upload_date = db.Column(db.DateTime, nullable=False)
    # ID of the user who uploaded this file (one-to-many)
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    # The user who uploaded this file (one-to-many)
    # See https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#one-to-many
    uploaded_by = db.relationship("User", back_populates="files")
    # File type
    filetype = db.Column(db.Enum(FileType), nullable=False)
    # Name of the file as it is stored on the system
    filename = db.Column(db.String, unique=True, nullable=False)
    # Size of the file, in bytes
    size = db.Column(db.Integer, nullable=False)
    # MD5 hash of the file contents
    hash = db.Column(db.String, unique=True, nullable=False, index=True)
    # The posts that reference this file
    # references = db.relationship('Post')

    def get_path(self) -> Path:
        return Path(current_app.static_folder) / self.filename

    def make_url(self, external: bool = True) -> str:
        return url_for("static", filename=self.filename, _external=external)

    def make_contract(self) -> FileContract:
        return FileContract(
            id=self.id,
            upload_name=self.upload_name,
            upload_date=self.upload_date,
            uploaded_by=self.uploaded_by.make_contract(),
            filetype=self.filetype,
            filename=self.filename,
            url=self.make_url(),
            size=self.size,
            hash=self.hash,
        )
