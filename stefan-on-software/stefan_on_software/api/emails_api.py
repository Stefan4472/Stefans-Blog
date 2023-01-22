import flask
import marshmallow
from flask import Response, current_app, request
from stefan_on_software.contracts.register_email import RegisterEmailContract
from stefan_on_software.email_provider import get_email_provider
from stefan_on_software.site_config import ConfigKeys

# Blueprint under which all views will be assigned
BLUEPRINT = flask.Blueprint("email", __name__, url_prefix="/api/v1/email")


@BLUEPRINT.route("/register", methods=["POST"])
def register_email():
    """Register a new email address for the email list."""
    if not current_app.config[ConfigKeys.USE_EMAIL_LIST]:
        current_app.logger.warn(
            "Received call to /register, but email is not configured"
        )
        return flask.Response(
            status=500,
            response="Email has not been configured by the web administrator",
        )

    try:
        contract = RegisterEmailContract.from_json(request.get_json())
    except marshmallow.exceptions.ValidationError:
        return Response(status=400, response="Invalid email address")

    try:
        get_email_provider().register_email(contract.address)
        return flask.Response(status=200)
    except ValueError as e:
        return flask.Response(status=500, response=str(e))
