from flask import current_app, render_template, url_for
import sib_api_v3_sdk
import datetime
from sib_api_v3_sdk.rest import ApiException
from flaskr.models.post import Post

# See:
# https://help.sendinblue.com/hc/en-us/articles/360000946299-About-Sendinblue-Template-Language
# https://help.sendinblue.com/hc/en-us/articles/4402386448530-Customize-your-emails-using-transactional-parameters

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

    def broadcast_new_post(self, post: Post) -> bool:
        """Creates and sends an email campaign notifying subscribers of the new post."""
        print('Broadcasting email campaign!')
        campaign_id = self._create_campaign(post)
        self._send_campaign(campaign_id)

    def _create_campaign(self, post: Post) -> int:
        """
        Create a campaign notifying subscribers of the given post.
        Returns the campaign ID. May throw ApiException!

        See https://developers.sendinblue.com/reference/createemailcampaign-1
        """
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = current_app.config['EMAIL_KEY']
        api_instance = sib_api_v3_sdk.EmailCampaignsApi(sib_api_v3_sdk.ApiClient(configuration))

        email_html = render_template(
            'email/new_post_email.html',
            # header_image=url_for('static', filename='site-banner.jpg', _external=True),
            header_url='https://www.stefanonsoftware.com/static/site-banner.JPG',
            post=post,
        )
        print(email_html)

        try:
            # Note: here is how you would set the "scheduled_at" time directly in the API call:
            # send_time = datetime.datetime.now(datetime.timezone.utc)
            # CreateEmailCampaign.scheduled_at = send_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z',
            api_response = api_instance.create_email_campaign(sib_api_v3_sdk.CreateEmailCampaign(
                tag='New Post',
                sender={"name": 'Stefan Kussmaul', "email": 'stefan@stefanonsoftware.com'},
                name=f'New Post - {post.title}',
                html_content=email_html,
                subject='A new post from StefanOnSoftware!',
                reply_to='stefan@stefanonsoftware.com',
                recipients={'listIds': [current_app.config['EMAIL_LIST_ID']]},
            ))
            print(api_response)
            return api_response.id
        except ApiException as e:
            print("Exception when calling EmailCampaignsApi->create_email_campaign: %s\n" % e)

    def _send_campaign(self, campaign_id: int):
        """Send the specified campaign now. May throw ApiException!"""
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = current_app.config['EMAIL_KEY']
        api_instance = sib_api_v3_sdk.EmailCampaignsApi(sib_api_v3_sdk.ApiClient(configuration))
        try:
            api_response = api_instance.send_email_campaign_now(campaign_id)
            print(api_response)
        except ApiException as e:
            print("Exception when calling EmailCampaignsApi->send_email_campaign_now: %s\n" % e)