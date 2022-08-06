from flask import current_app, render_template, url_for, g
import sib_api_v3_sdk
from sib_api_v3_sdk import ApiClient, ContactsApi, CreateContact, TransactionalEmailsApi, SendSmtpEmail
from sib_api_v3_sdk.rest import ApiException
from flaskr.models.post import Post


class EmailProvider:
    """
    Provides functionality for the site's email list. Uses the Sendinblue API.

    Do not instantiate this directly. Instead, call `get_email_provider()`
    to get an instance on the executing web thread.

    Note: see here for information on Sendinblue template parameters
    https://help.sendinblue.com/hc/en-us/articles/360000946299-About-Sendinblue-Template-Language

    TODO: better exception handling
    TODO: update Requirements.txt
    """
    def __init__(self, api_key: str, list_id: int):
        self._config = sib_api_v3_sdk.Configuration()
        self._config.api_key['api-key'] = api_key
        self._list_id = list_id

    def register_email(self, address: str) -> bool:
        """
        Register a new email address to the subscriber list. Returns whether successful.

        See https://developers.sendinblue.com/reference/createcontact
        """
        api = ContactsApi(ApiClient(self._config))
        try:
            api.create_contact(CreateContact(
                email=address,
                update_enabled=True,
                list_ids=[self._list_id],
            ))
        except ApiException as e:
            print(f'Exception when calling ContactsApi->create_contact: {e}')
            return False
        try:
            self._send_welcome_email(address)
        except ApiException as e:
            return False

    def _send_welcome_email(self, address: str):
        """
        Send a transactional "welcome" email to the specified address.
        May throw ApiException!

        See https://developers.sendinblue.com/reference/sendtransacemail
        """
        api = TransactionalEmailsApi(ApiClient(self._config))

        # Render the email in HTML
        email_html = render_template(
            'email/welcome_email.html',
            # TODO: don't hardcode this URL. Need a global configuration that sets the filename.
            # header_image=url_for('static', filename='site-banner.jpg', _external=True),
            header_url='https://www.stefanonsoftware.com/static/site-banner.JPG',
            recipient=address,
        )

        api_response = api.send_transac_email(SendSmtpEmail(
            to=[{"email": address}],
            reply_to={"email": "stefan@stefanonsoftware.com", "name": "Stefan Kussmaul"},
            html_content=email_html,
            sender={"name": "Stefan Kussmaul", "email": "stefan@stefanonsoftware.com"},
            subject='Welcome to the StefanOnSoftware Email List!',
        ))
        print(api_response)

    def broadcast_new_post(self, post: Post) -> bool:
        """Creates and sends an email campaign notifying subscribers of the new post."""
        print('Broadcasting email campaign!')
        try:
            campaign_id = self._create_campaign(post)
        except ApiException as e:
            raise ValueError()

        try:
            self._send_campaign(campaign_id)
            return True
        except ApiException as e:
            raise ValueError()

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
            header_url=post.get_banner_image().get_url(external=True),
            post=post,
        )

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

    def _send_campaign(self, campaign_id: int):
        """Send the specified campaign now. May throw ApiException!"""
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = current_app.config['EMAIL_KEY']
        api_instance = sib_api_v3_sdk.EmailCampaignsApi(sib_api_v3_sdk.ApiClient(configuration))
        api_instance.send_email_campaign_now(campaign_id)


def get_email_provider() -> EmailProvider:
    """
    Get an instance of EmailProvider for the current thread.

    Throws ValueError if the current app is not configured for sending emails.
    """
    if not current_app.config['EMAIL_CONFIGURED']:
        raise ValueError('App has not been configured to use the email API')
    if 'email_provider' not in g:
        g.email_provider = EmailProvider(
            current_app.config['EMAIL_KEY'],
            current_app.config['EMAIL_LIST_ID'],
        )
    return g.email_provider
