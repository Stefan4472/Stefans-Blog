import marshmallow
from flask import Blueprint, Response, current_app, jsonify, request, send_file
from flask_login import current_user, login_required
from sqlalchemy import desc

import flaskr.api.util as util
from flaskr import post_manager
from flaskr.contracts.add_tag import AddTagContract
from flaskr.contracts.create_post import CreatePostContract
from flaskr.contracts.get_posts import GetPostsContract
from flaskr.contracts.update_post import UpdatePostContract
from flaskr.database import db
from flaskr.models.post import Post
from flaskr.models.tag import Tag
from flaskr.post_manager import (
    InsufficientPermission,
    InvalidFile,
    InvalidMarkdown,
    InvalidSlug,
    NoSuchPost,
)

# TODO: one thing I don't like about 'Post' is that the logic is spread out across different places: `post_api`, `post`, and `post_manager`


# Blueprint under which all views will be assigned
BLUEPRINT = Blueprint("posts", __name__, url_prefix="/api/v1/posts")


@BLUEPRINT.route("", methods=["GET"])
@login_required
def get_posts():
    """Get post information."""
    try:
        contract = GetPostsContract.from_json(request.args)
    except marshmallow.exceptions.ValidationError as e:
        return jsonify(f"Invalid parameters: {e}"), 400

    # Create query dynamically based on the parameters passed in the request
    query = Post.query
    if contract.is_featured is not None:
        query = query.filter(Post.is_featured == contract.is_featured)
    if contract.is_published is not None:
        query = query.filter(Post.is_published == contract.is_published)
    query = query.order_by(desc(Post.last_modified))
    res = query.paginate(
        page=contract.offset if contract.offset else 1,
        per_page=contract.limit if contract.limit else 20,
    )
    # Offset specified but no results: request is out of range
    if contract.offset and not res:
        return Response(404)
    return jsonify([post.make_contract().make_json() for post in res.items])


@BLUEPRINT.route("", methods=["POST"])
@login_required
def create_post():
    """Creates a new post."""
    try:
        contract = CreatePostContract.from_json(request.get_json())
    except marshmallow.exceptions.ValidationError as e:
        return jsonify(f"Invalid parameters: {e}"), 400

    try:
        post = post_manager.create_post(contract, current_user)
        return jsonify(post.make_contract().make_json()), 201
    except InvalidSlug:
        return jsonify("Slug is invalid or non-unique"), 400
    except InvalidFile as e:
        return jsonify(f"Invalid file_id {e.file_id}"), 400
    except Exception as e:
        current_app.logger.error(f"Unknown exception while creating post: {e}")
        return Response(status=500)


@BLUEPRINT.route("/<int:post_id>", methods=["GET"])
@login_required
def get_single_post(post_id: int):
    """Get a single post by its ID."""
    post = Post.query.filter_by(id=post_id).first()
    if not post:
        return Response(status=404)
    return jsonify(post.make_contract().make_json())


@BLUEPRINT.route("/<int:post_id>", methods=["PUT"])
@login_required
def update_post(post_id: int):
    try:
        contract = UpdatePostContract.from_json(request.get_json())
    except marshmallow.exceptions.ValidationError as e:
        return jsonify(f"Invalid parameters: {e}"), 400

    try:
        post = post_manager.update_post(post_id, contract, current_user)
        return jsonify(post.make_contract().make_json())
    except InvalidSlug:
        return jsonify("Slug is invalid or non-unique"), 400
    except InvalidFile as e:
        return jsonify(f"Invalid file_id {e.file_id}"), 400
    except InsufficientPermission:
        return Response(status=403)
    except NoSuchPost:
        return Response(status=404)
    except Exception as e:
        current_app.logger.error(f"Unknown exception while creating post: {e}")
        return Response(status=500)


@BLUEPRINT.route("/<int:post_id>", methods=["DELETE"])
@login_required
def delete_post(post_id: int):
    try:
        post_manager.delete_post(post_id, current_user)
        return Response(status=204)
    except InsufficientPermission:
        return Response(status=403)
    except NoSuchPost:
        return Response(status=404)


@BLUEPRINT.route("/<int:post_id>/content", methods=["GET"])
@login_required
def get_content(post_id: int):
    post = Post.query.filter_by(id=post_id).first()
    if not post:
        return Response(status=404)
    return send_file(post.get_markdown_path())


@BLUEPRINT.route("/<int:post_id>/content", methods=["POST"])
@login_required
def set_content(post_id: int):
    try:
        raw_markdown, _ = util.get_uploaded_file(request)
    except ValueError as e:
        return jsonify(e), 400

    try:
        post_manager.set_content(post_id, raw_markdown)
        return Response(status=204)
    except InvalidMarkdown as e:
        return jsonify(e), 400
    except Exception as e:
        current_app.logger.error(f"Unknown exception while setting content: {e}")
        return Response(status=500)


@BLUEPRINT.route("/<int:post_id>/tags", methods=["GET"])
@login_required
def get_tags(post_id: int):
    post = Post.query.filter_by(id=post_id).first()
    if not post:
        return Response(status=404)
    return jsonify([tag.make_contract().make_json() for tag in post.tags])


@BLUEPRINT.route("/<int:post_id>/tags", methods=["POST"])
@login_required
def add_tag(post_id: int):
    try:
        contract = AddTagContract.from_json(request.get_json())
    except marshmallow.exceptions.ValidationError as e:
        return jsonify(f"Invalid parameters: {e}"), 400

    post = Post.query.filter_by(id=post_id).first()
    if not post:
        return Response(status=404)
    tag = Tag.query.filter_by(slug=contract.tag).first()
    if not tag:
        return jsonify("No such tag"), 400

    if tag not in post.tags:
        post.tags.append(tag)
        db.session.commit()
    return Response(status=204)


@BLUEPRINT.route("/<int:post_id>/tags/<string:tag>", methods=["DELETE"])
@login_required
def remove_tag(post_id: int, tag: str):
    post = Post.query.filter_by(id=post_id).first()
    if not post:
        return Response(status=404)
    if tag in (t.slug for t in post.tags):
        post.tags = [t for t in post.tags if t.slug != tag]
        db.session.commit()
        return Response(status=204)
    return Response(status=400)
