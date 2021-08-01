import pathlib
import hashlib
import datetime
import flask
from flask import Blueprint, current_app, request, Response
import werkzeug.exceptions
import werkzeug.utils
from sqlalchemy import asc, desc
from flaskr.database import db
from . import models
from . import util


# Blueprint under which all views will be assigned
API_BLUEPRINT = flask.Blueprint('api', __name__, url_prefix='/api/v1/')


# TODO: FIGURE OUT EXACT FLOW AND REQUEST TYPES (E.G. PUT VS POST)
# TODO: SETUP ACTUAL TESTING FRAMEWORK
@API_BLUEPRINT.route('/posts/<string:slug>', methods=['POST'])
def create_post(slug: str):
    config = request.get_json()
    print(config)
    post = models.Post(
        slug=slug,
        title=config['title'],
        byline=config['byline'],
        date=datetime.datetime.strptime(config['date'], "%m/%d/%y").date(),
    )
    print(post)

    for tag_name in config['tags']:
        tag_slug = util.generate_slug(tag_name)
        # Lookup tag in the database
        tag = models.Tag.query.filter_by(slug=tag_slug).first()
        # Create tag if doesn't exist already
        if not tag:
            tag = models.Tag(
                slug=tag_slug,
                name=tag_name,
                color=util.generate_random_color(),
            )
            # db.session.add(tag)
        # Register the post under this tag
        tag.posts.append(post)
    # db.session.add(post)
    # db.session.commit()

    dir_path = pathlib.Path(flask.current_app.static_folder) / slug
    dir_path.mkdir(exist_ok=True)

    return Response(status=200)


@API_BLUEPRINT.route('/posts/<string:slug>/body', methods=['POST'])
def upload_html(slug: str):
    print(request.files)

    file = request.files['file']
    safe_filename = werkzeug.utils.secure_filename(file.filename)
    print(safe_filename)

    # Save HTML file as 'post.html'
    dir_path = pathlib.Path(flask.current_app.static_folder) / slug
    file_path = dir_path / 'post.html'
    with open(file_path, 'wb+') as writef:
        file.save(writef)
    return Response(status=200)


@API_BLUEPRINT.route('/posts/<string:slug>/images', methods=['POST'])
def upload_images(slug: str):
    print('Yo')
    dir_path = pathlib.Path(flask.current_app.static_folder) / slug
    for file in request.files.values():
        print(file)
        # safe_filename = werkzeug.utils.secure_filename(file.filename)
        file_path = dir_path / file.filename

        img = file.read()
        md5 = hashlib.md5(img).hexdigest()
        print(md5)
        file.close()

        with open(file_path, 'wb+') as writef:
            writef.write(img)
    return Response(status=200)
