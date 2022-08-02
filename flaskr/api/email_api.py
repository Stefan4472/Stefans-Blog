import flask
from flask import request, Response
import marshmallow
from flaskr.contracts.register_email import RegisterEmailContract
from flaskr.email_provider import EmailProvider


# Blueprint under which all views will be assigned
BLUEPRINT = flask.Blueprint('email', __name__, url_prefix='/api/v1/email')


@BLUEPRINT.route('/register', methods=['POST'])
def register_email():
    """Register a new email address for the email list."""
    try:
        contract = RegisterEmailContract.from_json(request.get_json())
        # print(f'Got contract {contract}')
    except marshmallow.exceptions.ValidationError as e:
        return Response(status=400, response='Invalid parameters: {}'.format(e))

    provider = EmailProvider()
    success = provider.register_email(contract.address)
    return flask.Response(status=200 if success else 500)
