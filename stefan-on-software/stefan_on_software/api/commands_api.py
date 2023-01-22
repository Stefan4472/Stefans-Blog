import marshmallow
from flask import Blueprint, Response, current_app, request
from flask_login import login_required
from stefan_on_software import post_manager
from stefan_on_software.contracts.publish_post import PublishPostContract
from stefan_on_software.post_manager import NoSuchPost

# Blueprint under which all views will be assigned
BLUEPRINT = Blueprint("commands", __name__, url_prefix="/api/v1/commands")


@BLUEPRINT.route("/publish", methods=["POST"])
@login_required
def publish_post():
    try:
        contract = PublishPostContract.from_json(request.get_json())
    except marshmallow.exceptions.ValidationError as e:
        return Response(status=400, response="Invalid parameters: {}".format(e))

    try:
        post_manager.publish(contract.post_id, contract.send_email)
        return Response(status=204)
    except NoSuchPost:
        return Response(status=404)
    except Exception as e:
        current_app.logger.error(
            f"Unknown exception while publishing post with id={contract.post_id}: {e}"
        )
        return Response(status=500)


@BLUEPRINT.route("/unpublish", methods=["POST"])
@login_required
def unpublish_post():
    post_id = request.get_json().get("post_id")
    if not post_id:
        return Response(status=400, response="Missing post_id")
    try:
        post_manager.unpublish(post_id)
        return Response(status=204)
    except NoSuchPost:
        return Response(status=404)
    except Exception as e:
        current_app.logger.error(
            f"Unknown exception while un-publishing post with id={post_id}: {e}"
        )
        return Response(status=500)


@BLUEPRINT.route("/feature", methods=["POST"])
@login_required
def feature_post():
    post_id = request.get_json().get("post_id")
    if not post_id:
        return Response(status=400, response="Missing post_id")
    try:
        post_manager.set_featured(post_id, True)
        return Response(status=204)
    except NoSuchPost:
        return Response(status=404)
    except Exception as e:
        current_app.logger.error(
            f"Unknown exception while featuring post with id={post_id}: {e}"
        )
        return Response(status=500)


@BLUEPRINT.route("/unfeature", methods=["POST"])
@login_required
def unfeature_post():
    post_id = request.get_json().get("post_id")
    if not post_id:
        return Response(status=400, response="Missing post_id")
    try:
        post_manager.set_featured(post_id, False)
        return Response(status=204)
    except NoSuchPost:
        return Response(status=404)
    except Exception as e:
        current_app.logger.error(
            f"Unknown exception while featuring post with id={post_id}: {e}"
        )
        return Response(status=500)
