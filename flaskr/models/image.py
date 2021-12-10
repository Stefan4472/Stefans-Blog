import pathlib
import flask
from flaskr import db


class Image(db.Model):
    __tablename__ = 'images'
    filename = db.Column(db.String, primary_key=True)
    # User-given name at time of upload
    upload_name = db.Column(db.String, nullable=False)
    upload_date = db.Column(db.DateTime, nullable=False)
    # File extension
    extension = db.Column(db.String, nullable=False)
    # MD5 hash
    hash = db.Column(db.String, nullable=False)
    # Image dimensions (pixels)
    width = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    def get_path(self) -> pathlib.Path:
        return pathlib.Path(flask.current_app.static_folder) / self.filename
