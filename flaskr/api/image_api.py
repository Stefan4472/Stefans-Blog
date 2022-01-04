import hashlib
import flask
import io
import os
import pathlib
import uuid
import datetime as dt
from flask import request, Response, current_app
from flask_login import login_required
from PIL import UnidentifiedImageError, Image as PilImage
import werkzeug.exceptions
import werkzeug.utils
from flaskr.database import db
from flaskr.models.image import Image
from flaskr.api.util import get_uploaded_file


BLUEPRINT = flask.Blueprint('images', __name__, url_prefix='/api/v1/images')


@BLUEPRINT.route('', methods=['POST'])
@login_required
def upload_image():
    """Upload an image."""
    try:
        raw_image, upload_name = get_uploaded_file(request)
    except ValueError as e:
        return Response(status=400, response=str(e))

    # Check if an image with the same hash has already been uploaded.
    # If so, return the details of the already existing copy.
    file_hash = hashlib.md5(raw_image).hexdigest()
    query = Image.query.filter_by(hash=file_hash)
    if query.first():
        return flask.jsonify(query.first().to_dict())

    try:
        image = PilImage.open(io.BytesIO(raw_image))
    except UnidentifiedImageError:
        return Response(status=400, response='Cannot read file (improper format)')

    # Generate random UUID
    image_id = uuid.uuid4().hex
    safe_name = werkzeug.utils.secure_filename(upload_name)
    extension = os.path.splitext(safe_name)[-1]
    filename = image_id + extension

    # Write out
    write_path = pathlib.Path(flask.current_app.static_folder) / filename
    with open(write_path, 'wb+') as out:
        out.write(raw_image)

    record = Image(
        id=image_id,
        filename=filename,
        upload_name=safe_name,
        upload_date=dt.datetime.now(),
        extension=extension,
        hash=file_hash,
        width=image.width,
        height=image.height,
        size=os.path.getsize(write_path),
    )

    db.session.add(record)
    db.session.commit()
    return flask.jsonify(record.to_dict())


@BLUEPRINT.route('/<string:image_id>', methods=['GET'])
def download_image(image_id: str):
    image = Image.query.filter_by(id=image_id).first()
    if not image:
        return Response(status=404)
    return flask.send_file(
        image.get_path(),
        as_attachment=True,
        attachment_filename=image.upload_name,
    )


@BLUEPRINT.route('/<string:image_id>/metadata', methods=['GET'])
def get_metadata(image_id: str):
    image = Image.query.filter_by(id=image_id).first()
    if not image:
        return Response(status=404)
    return flask.jsonify(image.to_dict())


@BLUEPRINT.route('/<string:image_id>', methods=['DELETE'])
@login_required
def delete_image(image_id: str):
    """Delete image with specified ID."""
    record = Image.query.filter_by(id=image_id).first()
    if not record:
        return Response(status=404)

    if record.images:
        msg = "Can't delete because image is referenced in at least one post"
        return Response(status=400, response=msg)

    # Delete file and remove from database
    try:
        record.get_path().unlink()
    except FileNotFoundError:
        # If file isn't found, that means something weird happened,
        # but we don't really care at this point.
        pass

    db.session.delete(record)
    db.session.commit()
    return Response(status=200)
