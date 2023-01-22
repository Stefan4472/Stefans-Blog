import marshmallow
import stefan_on_software.api.util as util
from flask import Blueprint, Response, jsonify, request
from flask_login import login_required
from stefan_on_software.contracts.create_tag import CreateTagContract
from stefan_on_software.contracts.update_tag import UpdateTagContract
from stefan_on_software.database import db
from stefan_on_software.models.tag import Tag

# Blueprint under which all views will be assigned
BLUEPRINT = Blueprint("tags", __name__, url_prefix="/api/v1/tags")


@BLUEPRINT.route("", methods=["GET"])
@login_required
def get_all_tags():
    """Get all tags that have been created."""
    return jsonify([tag.make_contract().make_json() for tag in Tag.query.all()])


@BLUEPRINT.route("", methods=["POST"])
@login_required
def create_tag():
    """Create a tag."""
    try:
        contract = CreateTagContract.from_json(request.get_json())
    except marshmallow.exceptions.ValidationError as e:
        return jsonify(f"Invalid parameters: {e.messages}"), 400

    tag = Tag.query.filter_by(slug=contract.slug).first()
    if tag:
        return jsonify("The desired slug is not unique"), 400

    tag = Tag(
        slug=contract.slug,
        name=contract.name,
        description=contract.description,
        color=contract.color if contract.color else util.generate_random_color(),
    )
    db.session.add(tag)
    db.session.commit()
    return jsonify(tag.make_contract().make_json()), 201


@BLUEPRINT.route("/<string:tag>", methods=["GET"])
@login_required
def get_single_tag(tag: str):
    """Get a single tag by its slug."""
    tag = Tag.query.filter_by(slug=tag).first()
    if not tag:
        return Response(status=404)
    return jsonify(tag.make_contract().make_json())


@BLUEPRINT.route("/<string:tag>", methods=["POST"])
@login_required
def update_tag(tag: str):
    """Change a tag, given the tag's slug."""
    tag = Tag.query.filter_by(slug=tag).first()
    if not tag:
        return Response(status=404)

    try:
        contract = UpdateTagContract.from_json(request.get_json())
    except marshmallow.exceptions.ValidationError as e:
        return jsonify(f"Invalid parameters: {e}"), 400

    tag.name = contract.name
    tag.description = contract.description
    tag.color = contract.color
    db.session.commit()
    return jsonify(tag.make_contract().make_json()), 200


@BLUEPRINT.route("/<string:tag>", methods=["DELETE"])
@login_required
def delete_tag(tag: str):
    """Delete a tag, given the tag's slug."""
    tag = Tag.query.filter_by(slug=tag).first()
    if not tag:
        return Response(status=404)

    db.session.delete(tag)
    db.session.commit()
    return Response(status=204)
