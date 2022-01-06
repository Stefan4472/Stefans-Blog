import io
import flask
import datetime as dt
import typing
import os
import pathlib
import uuid
from PIL import Image as PilImage, UnidentifiedImageError
from flaskr import db
import flaskr.api.constants as constants
import flaskr.api.util as util


class Image(db.Model):
    __tablename__ = 'image'
    id = db.Column(db.String, primary_key=True)
    filename = db.Column(db.String, unique=True, nullable=False)
    format = db.Column(db.String, nullable=False)
    # User-given name at time of upload
    upload_name = db.Column(db.String, nullable=False)
    upload_date = db.Column(db.DateTime, nullable=False)
    # MD5 hash of the original upload. Used internally to check for duplicates.
    hash = db.Column(db.String, nullable=False)
    # Image dimensions (pixels)
    width = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    # Size (bytes)
    size = db.Column(db.Integer, nullable=False)

    def __init__(
            self,
            raw_image: bytes,
            upload_name: str,
            upload_date: dt.datetime,
    ):
        # Note: some code here is non-optimal because Pillow doesn't handle GIFs
        # well. So, we use the Pillow Image instance for processing, but
        # actually save off the raw_image in the case of a GIF.
        # Ideally, we would take a Pillow image instance in the constructor
        # and handle all images in a common pipeline.
        try:
            image = PilImage.open(io.BytesIO(raw_image))
        except UnidentifiedImageError:
            raise ValueError('Cannot read image (improper format)')

        # Generate random UUID
        self.id = uuid.uuid4().hex
        self.upload_name = upload_name
        self.upload_date = upload_date
        # Calculate the hash of the *original* image
        self.hash = util.calc_hash(raw_image)
        # Process the image. Non-gifs will be converted to JPEG
        processed_image, new_format, new_extension = self._process_image(image)
        self.filename = self.id + new_extension
        self.format = new_format
        self.width = processed_image.width
        self.height = processed_image.height
        # For GIFs, save raw bytes, otherwise use Pillow's `save()`.
        # See notes above.
        if new_format == 'GIF':
            with open(self.get_path(), 'wb+') as out:
                out.write(raw_image)
        else:
            processed_image.save(self.get_path(), new_format)
        self.size = os.path.getsize(self.get_path())

    @staticmethod
    def _process_image(image: PilImage) -> typing.Tuple['PilImage', str, str]:
        """
        Potentially convert to JPEG and reduce size.
        Return tuple of resulting image, image format, and image extension.
        """
        # Do nothing to GIFs
        if image.format == 'GIF':
            return image, 'GIF', '.gif'
        # Convert still images to JPEG and limit to MAX_IMG_SIZE
        else:
            # Bound to MAX_IMG_SIZE
            if image.width > constants.MAX_IMG_SIZE[0] or image.height > constants.MAX_IMG_SIZE[1]:
                image = image.thumbnail(constants.MAX_IMG_SIZE, PilImage.ANTIALIAS)
            # Convert to RGB (for saving to JPEG)
            image = image.convert('RGB')
            return image, 'JPEG', '.jpg'

    def get_path(self) -> pathlib.Path:
        return pathlib.Path(flask.current_app.static_folder) / self.filename

    def get_url(self) -> str:
        return flask.url_for('static', filename=self.filename)

    def to_dict(self) -> dict:
        """Return dictionary representation that can be used to create JSON."""
        return {
            'id': self.id,
            'filename': self.filename,
            'format': self.format,
            'name': self.upload_name,
            'upload_date': str(self.upload_date),
            'width': self.width,
            'height': self.height,
            'size': self.size,
            'url': self.get_url(),
        }
