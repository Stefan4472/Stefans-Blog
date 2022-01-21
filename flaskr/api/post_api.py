import shutil
import flask
import marshmallow
import typing
import sqlalchemy
from flask import request, Response, Blueprint, jsonify, current_app
from flask_login import login_required
import flaskr.api.constants as constants
import flaskr.api.util as util
from flaskr.database import db
from flaskr.models.post import Post
from flaskr.models.image import Image
from flaskr.models.tag import Tag
from flaskr.contracts.create_post import CreatePostContract
from flaskr.contracts.update_post import UpdatePostContract
from flaskr.contracts.patch_post import PatchPostContract
# TODO: Should have a set of Tag endpoints too
# TODO: SETUP TESTING FRAMEWORK
# TODO: log all SQLAlchemy errors


# Blueprint under which all views will be assigned
BLUEPRINT = Blueprint('posts', __name__, url_prefix='/api/v1/posts')


@BLUEPRINT.route('/', methods=['GET'])
@login_required
def get_posts():
    """
    Get a JSON "manifest" of posts.

    Query parameters:
    (bool) `featured`: return only posts where is_featured = ?
    (bool) `published`: return only posts where is_published = ?
    """
    # Create query dynamically based on the parameters passed in the request
    query = Post.query
    if constants.KEY_FEATURE in request.args:
        as_bool = (request.args[constants.KEY_FEATURE].lower() == 'true')
        query = query.filter(Post.is_featured == as_bool)
    if constants.KEY_PUBLISH in request.args:
        as_bool = (request.args[constants.KEY_PUBLISH].lower() == 'true')
        query = query.filter(Post.is_published == as_bool)

    manifest = {}
    for post in query.all():
        manifest[post.slug] = post.to_dict()
    return jsonify({'posts': manifest})


# Commit #1: Change create_post and the site_manager logic. Get it working
# Commit #2: Add PUT (edit) and PATCH methods. Change `Post` model to require all args on creation
# Commit #3: cleanup (especially sitemanager)
@BLUEPRINT.route('', methods=['POST'])
@login_required
def create_post():
    """
    Creates a post with the specified configuration and an empty Markdown
    text.

    I wanted to make this endpoing also require a Markdown file upload,
    but accepting JSON data *and* an uploaded file is tricky. That's
    why I split the Markdown out into its own sub-resource.

    Returns 400 if a post with the given slug already exists.
    """
    try:
        contract = CreatePostContract.from_json(request.get_json())
    except marshmallow.exceptions.ValidationError as e:
        return Response(status=400, response='Invalid parameters: {}'.format(e))

    if Post.query.filter_by(slug=contract.slug).first():
        msg = 'A post with the given slug already exists'
        return Response(response=msg, status=400)

    try:
        post = Post(
            contract.slug,
            contract.title,
            get_image(contract.image),
            get_image(contract.banner),
            get_image(contract.thumbnail),
            byline=contract.byline,
            publish_date=contract.publish_date,
            is_featured=contract.feature,
            is_published=contract.publish,
            title_color=contract.title_color,
            tags=get_or_create_tags(contract.tags),
        )
        db.session.add(post)
        db.session.commit()
        return Response(status=200)
    except ValueError as e:
        return Response(status=400, response=str(e))
    except sqlalchemy.exc.SQLAlchemyError as e:
        print(e)
        return Response(status=500, response='Internal database error')


@BLUEPRINT.route('/<string:slug>', methods=['PUT'])
@login_required
def update_post(slug: str):
    try:
        contract = UpdatePostContract.from_json(request.get_json())
    except marshmallow.exceptions.ValidationError as e:
        return Response(status=400, response='Invalid parameters: {}'.format(e))

    post = Post.query.filter_by(slug=slug).first()
    if not post:
        return Response(status=404)

    try:
        post.title = contract.title
        post.set_featured_image(get_image(contract.image))
        post.set_banner_image(get_image(contract.banner))
        post.set_thumbnail_image(get_image(contract.thumbnail))
        if contract.byline:
            post.byline = contract.byline
        if contract.publish_date:
            post.publish_date = contract.publish_date
        if contract.feature is not None:
            post.is_featured = contract.feature
        if contract.publish is not None:
            post.is_published = contract.publish
        if contract.title_color:
            post.title_color = contract.title_color
        post.tags = get_or_create_tags(contract.tags)
        db.session.commit()
        return Response(status=200)
    except ValueError as e:
        return Response(status=400, response=str(e))
    except sqlalchemy.exc.SQLAlchemyError as e:
        return Response(status=500, response='Internal database error')


@BLUEPRINT.route('/<string:slug>', methods=['PATCH'])
@login_required
def patch_post(slug: str):
    try:
        contract = PatchPostContract.from_json(request.get_json())
    except marshmallow.exceptions.ValidationError as e:
        return Response(status=400, response='Invalid parameters: {}'.format(e))

    post = Post.query.filter_by(slug=slug).first()
    if not post:
        return Response(status=404)

    try:
        if contract.title:
            post.title = contract.title
        if contract.byline:
            post.byline = contract.byline
        if contract.publish_date:
            post.publish_date = contract.publish_date
        if contract.image:
            post.set_featured_image(get_image(contract.image))
        if contract.banner:
            post.set_banner_image(get_image(contract.banner))
        if contract.thumbnail:
            post.set_thumbnail_image(get_image(contract.thumbnail))
        if contract.tags:
            post.tags = get_or_create_tags(contract.tags)
        if contract.publish is not None:
            post.is_published = contract.publish
        if contract.feature is not None:
            post.is_featured = contract.feature
        if contract.title_color:
            post.set_title_color(contract.title_color)
        db.session.commit()
        return Response(status=200)
    except ValueError as e:
        return Response(status=400, response=str(e))
    except sqlalchemy.exc.SQLAlchemyError as e:
        return Response(status=500, response='Internal database error')


@BLUEPRINT.route('/<string:slug>/markdown', methods=['PUT'])
@login_required
def upload_markdown(slug: str):
    """Upload the Markdown body of the post."""
    post = Post.query.filter_by(slug=slug).first()
    if not post:
        return Response(status=404)
    try:
        raw_markdown, _ = util.get_uploaded_file(request)
    except ValueError as e:
        return Response(status=400, response=str(e))
    try:
        markdown = raw_markdown.decode('utf-8', errors='strict')
    except UnicodeError as e:
        msg = f'Error reading Markdown in UTF-8: {e}'
        return Response(status=400, response=msg)
    try:
        post.set_markdown(markdown)
    except ValueError as e:
        return Response(status=400, response=str(e))
    try:
        db.session.commit()
    except sqlalchemy.exc.SQLAlchemyError as e:
        return Response(status=500, response='Internal database error')
    return Response(status=200)


@BLUEPRINT.route('/<string:slug>/markdown', methods=['GET'])
@login_required
def download_markdown(slug: str):
    post = Post.query.filter_by(slug=slug).first()
    if not post:
        return Response(status=404)
    return flask.send_file(
        post.get_markdown_path(),
        as_attachment=True,
        attachment_filename=slug+'.md',
    )


@BLUEPRINT.route('/<string:slug>', methods=['DELETE'])
@login_required
def delete_post(slug: str):
    post = Post.query.filter_by(slug=slug).first()
    if not post:
        return Response(status=404)
    post.run_delete_logic()
    post.delete()
    db.session.commit()
    return Response(status=200)


def get_or_create_tags(tags: typing.List[str]) -> typing.List[Tag]:
    if tags:
        tag_objects: typing.List[Tag] = []
        for tag_name in tags:
            tag_slug = util.generate_slug(tag_name)
            tag_obj = Tag.query.filter_by(slug=tag_slug).first()
            # Create tag if doesn't exist already
            if not tag_obj:
                tag_obj = Tag(
                    slug=tag_slug,
                    name=tag_name,
                    color=util.generate_random_color(),
                )
                db.session.add(tag_obj)
            tag_objects.append(tag_obj)
        return tag_objects
    else:
        return []


def get_image(filename: str) -> Image:
    image = Image.query.filter_by(filename=filename).first()
    if not image:
        raise ValueError(f'Specified image "{filename}" not found on server')
    return image
