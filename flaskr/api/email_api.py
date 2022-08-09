import flask
from flask import request, Response, current_app
import marshmallow
from flaskr.contracts.register_email import RegisterEmailContract
from flaskr.email_provider import get_email_provider


# Blueprint under which all views will be assigned
BLUEPRINT = flask.Blueprint('email', __name__, url_prefix='/api/v1/email')


@BLUEPRINT.route('/register', methods=['POST'])
def register_email():
    """Register a new email address for the email list."""
    if not current_app.config['EMAIL_CONFIGURED']:
        current_app.logger.warn('Received call to /register, but email is not configured')
        return flask.Response(status=500, response='Email has not been configured by the web administrator')

    try:
        contract = RegisterEmailContract.from_json(request.get_json())
    except marshmallow.exceptions.ValidationError as e:
        return Response(status=400, response='Invalid email address')

    try:
        get_email_provider().register_email(contract.address)
        return flask.Response(status=200)
    except ValueError as e:
        return flask.Response(status=500, response=str(e))
