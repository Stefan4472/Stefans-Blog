from flask import current_app, render_template, url_for
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException


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
        # configuration = sib_api_v3_sdk.Configuration()
        # configuration.api_key['api-key'] = current_app.config['EMAIL_KEY']
        # api_instance = sib_api_v3_sdk.ContactsApi(sib_api_v3_sdk.ApiClient(configuration))

        try:
            # api_instance.create_contact(sib_api_v3_sdk.CreateContact(
            #     email=address,
            #     update_enabled=True,
            #     list_ids=[current_app.config['EMAIL_LIST_ID']],
            # ))
            self._send_welcome_email(address)
            return True
        except ApiException as e:
            print(f'Exception when calling ContactsApi->create_contact: {e}')
            return False

    def _send_welcome_email(self, address: str):
        """
        Send a transactional "welcome" email to the specified address.

        See https://developers.sendinblue.com/reference/sendtransacemail
        """
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = current_app.config['EMAIL_KEY']
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

        # Render the email in HTML
        email_html = render_template(
            'email/welcome_email.html',
            # header_image=url_for('static', filename='site-banner.jpg', _external=True),
            header_url='https://www.stefanonsoftware.com/static/site-banner.JPG',
            recipient=address,
        )

        try:
            api_response = api_instance.send_transac_email(sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": address}],
                reply_to={"email": "stefan@stefanonsoftware.com", "name": "Stefan Kussmaul"},
                html_content=email_html,
                sender={"name": "Stefan Kussmaul", "email": "stefan@stefanonsoftware.com"},
                subject='Welcome to the StefanOnSoftware Email List!',
            ))
            print(api_response)
        except ApiException as e:
            print("Exception when calling SMTPApi->send_transac_email: %s\n" % e)

    # def broadcast_email(self) -> bool:
