import marshmallow
from flask import request, Response, Blueprint, jsonify, current_app, send_file
from flask_login import login_required, current_user
from flaskr.models.post import Post
from flaskr.models.tag import Tag
from flaskr.contracts.create_or_update_post import CreateOrUpdatePostContract
from flaskr.contracts.get_posts import GetPostsContract
import flaskr.post_manager as post_manager
from flaskr.post_manager import NoSuchPost, InvalidSlug, InvalidFile, InsufficientPermission, ImproperState, InvalidMarkdown
import flaskr.api.util as util


# Blueprint under which all views will be assigned
BLUEPRINT = Blueprint('posts', __name__, url_prefix='/api/v1/posts')


@BLUEPRINT.route('/', methods=['GET'])
@login_required
def get_posts():
    """Get post information."""
    # TODO: paging
    try:
        contract = GetPostsContract.from_json(request.get_json())
    except marshmallow.exceptions.ValidationError as e:
        return Response(status=400, response='Invalid parameters: {}'.format(e))

    # Create query dynamically based on the parameters passed in the request
    query = Post.query
    if contract.is_featured is not None:
        query = query.filter(Post.is_featured == contract.is_featured)
    if contract.is_published is not None:
        query = query.filter(Post.is_published == contract.is_published)

    return jsonify([post.make_contract().make_json() for post in query.all()])


@BLUEPRINT.route('/', methods=['POST'])
@login_required
def create_post():
    """Creates a new post."""
    try:
        contract = CreateOrUpdatePostContract.from_json(request.get_json())
    except marshmallow.exceptions.ValidationError as e:
        return Response(status=400, response='Invalid parameters: {}'.format(e))

    try:
        post = post_manager.create_post(contract, current_user)
        return jsonify(post.make_contract().make_json()), 201
    except InvalidSlug:
        return Response(status=400, response='Slug is invalid or non-unique')
    except InvalidFile as e:
        return Response(status=400, response=f'Invalid file_id {e.file_id}')
    except Exception as e:
        current_app.logger.error(f'Unknown exception while creating post: {e}')
        return Response(status=500)


@BLUEPRINT.route('/<int:post_id>', methods=['GET'])
@login_required
def get_single_post(post_id: int):
    """Get a single post by its ID."""
    post = Post.query.filter_by(id=post_id).first()
    if not post:
        return Response(status=404)
    return jsonify(post.make_contract().make_json())


@BLUEPRINT.route('/<int:post_id>', methods=['PUT'])
@login_required
def update_post(post_id: int):
    try:
        contract = CreateOrUpdatePostContract.from_json(request.get_json())
    except marshmallow.exceptions.ValidationError as e:
        return Response(status=400, response='Invalid parameters: {}'.format(e))

    try:
        post = post_manager.update_post(post_id, contract, current_user)
        return jsonify(post.make_contract().make_json())
    except NoSuchPost:
        return Response(status=404)
    except InvalidSlug:
        return Response(status=400, response='Slug is invalid or non-unique')
    except InvalidFile as e:
        return Response(status=400, response=f'Invalid file_id {e.file_id}')
    except InsufficientPermission:
        return Response(status=403)
    except ImproperState:
        return Response(status=400, response='Invalid state')
    except Exception as e:
        current_app.logger.error(f'Unknown exception while creating post: {e}')
        return Response(status=500)


@BLUEPRINT.route('/<int:post_id>', methods=['DELETE'])
@login_required
def delete_post(post_id: int):
    try:
        post_manager.delete_post(post_id, current_user)
        return Response(status=204)
    except NoSuchPost:
        return Response(status=404)
    except InsufficientPermission:
        return Response(status=403)


@BLUEPRINT.route('/<int:post_id>/content', methods=['GET'])
@login_required
def get_content(post_id: int):
    post = Post.query.filter_by(id=post_id).first()
    if not post:
        return Response(status=404)
    return send_file(post.get_markdown_path())


@BLUEPRINT.route('/<int:post_id>/content', methods=['POST'])
@login_required
def set_content(post_id: int):
    try:
        raw_markdown, _ = util.get_uploaded_file(request)
    except ValueError as e:
        return Response(status=400, response=str(e))
    try:
        post_manager.set_content(post_id, raw_markdown)
        return Response(status=204)
    except InvalidMarkdown as e:
        return Response(status=400, response=str(e))
    except Exception as e:
        current_app.logger.error(f'Unknown exception while setting content: {e}')
        return Response(status=500)


'''
# try:
#     if contract.send_email and current_app.config[ConfigKeys.USE_EMAIL_LIST]:
#         get_email_provider().broadcast_new_post(post)
#     elif contract.send_email:
#         current_app.logger.warn('send_email=True but no email service is configured')
# except ValueError as e:
#     current_app.logger.error(f'Error while sending email notification: {e}')
#     return Response(status=400, response=str(e))
# return Response(status=200)
'''