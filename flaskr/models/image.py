import pathlib
import flask
from flaskr import db


class Image(db.Model):
    __tablename__ = 'image'
    id = db.Column(db.String, primary_key=True)
    filename = db.Column(db.String, unique=True, nullable=False)
    # File extension
    extension = db.Column(db.String, nullable=False)
    # User-given name at time of upload
    upload_name = db.Column(db.String, nullable=False)
    upload_date = db.Column(db.DateTime, nullable=False)
    # MD5 hash
    hash = db.Column(db.String, nullable=False)
    # Image dimensions (pixels)
    width = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    # Size (bytes)
    size = db.Column(db.Integer, nullable=False)

    def get_path(self) -> pathlib.Path:
        return pathlib.Path(flask.current_app.static_folder) / self.filename

    def get_url(self) -> str:
        return flask.url_for('static', filename=self.filename)

    def to_dict(self) -> dict:
        """Return dictionary representation that can be used to create JSON."""
        return {
            'id': self.id,
            'filename': self.filename,
            'extension': self.extension,
            'name': self.upload_name,
            'upload_date': str(self.upload_date),
            'hash': self.hash,
            'width': self.width,
            'height': self.height,
            'size': self.size,
            'url': self.get_url(),
        }
