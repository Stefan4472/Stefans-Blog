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


BLUEPRINT = flask.Blueprint('images', __name__, url_prefix='/api/v1/images')
# TODO: A `GET` ENDPOINT


@BLUEPRINT.route('', methods=['POST'])
@login_required
def upload_image():
    """Upload an image."""
    if len(request.files) == 0:
        return Response(status=400, response='No file uploaded')
    elif len(request.files) > 1:
        return Response(status=400, response='More than one file uploaded')

    # Read image and calculate hash
    file = list(request.files.values())[0]
    raw_img = file.read()
    filehash = hashlib.md5(raw_img).hexdigest()
    file.close()

    # Check if an image with the given hash has already been uploaded.
    # If so, return the filename of the already existing copy.
    query = Image.query.filter_by(hash=filehash)
    if query.first():
        print(query.first().filename)
        return flask.jsonify(query.first().filename)

    try:
        image = PilImage.open(io.BytesIO(raw_img))
    except UnidentifiedImageError:
        return Response(status=400, response='Cannot read file (improper format)')

    safe_name = werkzeug.utils.secure_filename(file.filename)
    extension = os.path.splitext(safe_name)[-1]

    # Note that we generate a UUID filename for the image
    record = Image(
        filename=uuid.uuid4().hex + extension,
        upload_name=safe_name,
        upload_date=dt.datetime.now(),
        extension=extension,
        hash=filehash,
        width=image.width,
        height=image.height,
    )

    # Write out
    write_path = pathlib.Path(flask.current_app.static_folder) / record.filename
    with open(write_path, 'wb+') as out:
        out.write(raw_img)

    db.session.add(record)
    db.session.commit()
    return flask.jsonify(record.filename)


@BLUEPRINT.route('/<string:filename>', methods=['DELETE'])
@login_required
def delete_image(filename: str):
    """Delete image with specified filename."""
    record = Image.query.filter_by(filename=filename).first()
    if not record:
        return Response(status=404)

    if record.images_new:
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
