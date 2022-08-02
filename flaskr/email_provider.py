from flask import current_app
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
import time


class EmailProvider:
    def __init__(self):
        pass

    def register_email(self, address: str) -> bool:
        """
        Register a new email address to the subscriber list. Returns whether successful.

        See https://developers.sendinblue.com/reference/createcontact
        """
        if not (current_app.config['EMAIL_KEY'] and current_app.config['EMAIL_LIST_ID']):
            print('No email provider configured')  # TODO: log a warning
            return False

        print(f'Registering address {address}')
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = current_app.config['EMAIL_KEY']
        api_instance = sib_api_v3_sdk.ContactsApi(sib_api_v3_sdk.ApiClient(configuration))

        try:
            api_instance.create_contact(sib_api_v3_sdk.CreateContact(
                email=address,
                update_enabled=True,
                list_ids=[current_app.config['EMAIL_LIST_ID']],
            ))
            return True
        except ApiException as e:
            print(f'Exception when calling ContactsApi->create_contact: {e}')
            return False
