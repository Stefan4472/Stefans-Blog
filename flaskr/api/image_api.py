import flask
import datetime as dt
from flask import request, Response, current_app
from flask_login import login_required
import werkzeug.exceptions
import werkzeug.utils
from flaskr.database import db
from flaskr.models.image import Image
import flaskr.api.util as util


BLUEPRINT = flask.Blueprint('images', __name__, url_prefix='/api/v1/images')


@BLUEPRINT.route('', methods=['POST'])
@login_required
def upload_image():
    """Upload an image."""
    try:
        raw_image, upload_name = util.get_uploaded_file(request)
        current_app.logger.debug(f'Uploading image with filename {upload_name}')
    except ValueError as e:
        return Response(status=400, response=str(e))

    # Check if an image with the same hash has already been uploaded.
    # If so, return the details of the already existing copy.
    img_hash = util.calc_hash(raw_image)
    query = Image.query.filter_by(hash=img_hash)
    if query.first():
        current_app.logger.debug(f'Image is a duplicate of {query.first().id}')
        return flask.jsonify(query.first().to_dict())

    try:
        record = Image(
            raw_image,
            werkzeug.utils.secure_filename(upload_name),
            dt.datetime.now(),
        )
        db.session.add(record)
        db.session.commit()
        current_app.logger.info(f'Successfully uploaded image with id={record.id}')
        return flask.jsonify(record.to_dict())
    except ValueError as e:  # Note: ValueError is a little broad
        return Response(status=400, response=str(e))


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

    current_app.logger.debug(f'Got request to delete image with id={image_id}')
    if record.images:
        msg = "Can't delete because image is referenced in at least one post"
        current_app.logger.debug(msg)
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
    current_app.logger.info(f'Deleted image with id={image_id}')
    return Response(status=200)
