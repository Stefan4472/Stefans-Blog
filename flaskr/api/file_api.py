import flask
from flask import request, Response, current_app, jsonify
from flask_login import login_required, current_user
from flaskr.database import db
from flaskr.models.file import File
import flaskr.file_manager as file_manager
# TODO: "references" endpoint

BLUEPRINT = flask.Blueprint('files', __name__, url_prefix='/api/v1/files')


@BLUEPRINT.route('/', methods=['GET'])
@login_required
def get_files():
    """Get files that have been uploaded."""
    return jsonify([f.make_contract().make_json() for f in File.query.all()])


@BLUEPRINT.route('/', methods=['POST'])
@login_required
def upload_file():
    """Upload a file"""
    if not request.files:
        return Response('No file uploaded', status=400)
    elif len(request.files) > 1:
        return Response('More than one file uploaded', status=400)

    try:
        file = list(request.files.values())[0]
        created = file_manager.store_file(file, current_user)
        return jsonify(created.make_contract().make_json()), 201
    except file_manager.InvalidExtension:
        return Response('Unsupported or missing file extension', status=400)
    except file_manager.FileAlreadyExists as e:
        return jsonify(e.duplicate.make_contract().make_json()), 200
    except Exception as e:
        print(e.args)
        current_app.logger.error(f'Unknown exception while storing file: {e}')
        return Response(status=500)


@BLUEPRINT.route('/<string:file_id>', methods=['GET'])
def download_file(file_id: str):
    file = File.query.filter_by(id=file_id).first()
    if not file:
        return Response(status=404)
    return flask.send_file(file.get_path())


@BLUEPRINT.route('/<string:file_id>', methods=['DELETE'])
def delete_file(file_id: str):
    file = File.query.filter_by(id=file_id).first()
    if not file:
        return Response(status=404)
    file_manager.delete_file(file)
    return Response(status=204)


@BLUEPRINT.route('/<string:file_id>/metadata', methods=['GET'])
def get_file_metadata(file_id: str):
    file = File.query.filter_by(id=file_id).first()
    if not file:
        return Response(status=404)
    return jsonify(file.make_contract().make_json())
