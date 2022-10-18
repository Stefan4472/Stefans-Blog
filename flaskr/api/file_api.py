import flask
import datetime as dt
from flask import request, Response, current_app, jsonify
from flask_login import login_required, current_user
import werkzeug.exceptions
import werkzeug.utils
from flaskr.database import db
from flaskr.models.image import Image
import flaskr.api.util as util
from flaskr.models.file import File
import flaskr.file_manager as file_manager

BLUEPRINT = flask.Blueprint('files', __name__, url_prefix='/api/v1/files')


@BLUEPRINT.route('/', methods=['GET'])
@login_required
def get_files():
    """Get files that have been uploaded."""
    return jsonify(f.make_contract().to_json() for f in File.query.all())


@BLUEPRINT.route('/', methods=['POST'])
@login_required
def upload_file():
    """Upload a file"""
    if not request.files:
        return Response('No file uploaded', status=400)
    elif len(request.files) > 1:
        return Response('More than one file uploaded', status=400)

    try:
        # Get the uploaded file from the request
        file = list(request.files.values())[0]
        created = file_manager.store_file(file, current_user)
        print(created)
        print(created.make_contract())
        print(created.make_contract().make_json())
        return jsonify(created.make_contract().make_json()), 201
    except file_manager.InvalidExtension:
        return Response('Unsupported or missing file extension', status=400)
    except file_manager.FileAlreadyExists as e:
        return jsonify(e.duplicate.make_contract().make_json()), 200
    except Exception as e:
        current_app.logger.error(f'Unknown exception while storing file: {e}')
        return Response(status=500)
