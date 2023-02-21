import sib_api_v3_sdk
from flask import current_app, g, render_template
from sib_api_v3_sdk import (
    ApiClient,
    ContactsApi,
    CreateContact,
    CreateEmailCampaign,
    EmailCampaignsApi,
    SendSmtpEmail,
    TransactionalEmailsApi,
)
from sib_api_v3_sdk.rest import ApiException
from stefan_on_software.models.post import Post

from .site_config import ConfigKeys


# TODO: better failure handling. The problem is, I don't know under what conditions the Sendinblue API will fail
class EmailProvider:
    """
    Provides functionality for the site's email list. Uses the Sendinblue API.

    Do not instantiate this directly. Instead, call `get_email_provider()`
    to get an instance on the executing web thread.

    Note: see here for information on Sendinblue template parameters
    https://help.sendinblue.com/hc/en-us/articles/360000946299-About-Sendinblue-Template-Language
    """

    def __init__(self, api_key: str, list_id: int):
        self._config = sib_api_v3_sdk.Configuration()
        self._config.api_key["api-key"] = api_key
        self._list_id = list_id

    def _make_client(self) -> ApiClient:
        """Make and return an ApiClient instance using configured values."""
        return ApiClient(self._config)

    def register_email(self, address: str):
        """
        Register a new email address to the subscriber list.
        May raise ValueError.
        """
        current_app.logger.debug("Registering an email address")
        self._create_contact(address)
        self._send_welcome_email(address)
        current_app.logger.debug("Email has been registered successfully")

    def _create_contact(self, address: str):
        """
        Add the specified email address to the contact list.
        May raise ValueError.

        See https://developers.sendinblue.com/reference/createcontact
        """
        api = ContactsApi(self._make_client())
        try:
            api.create_contact(
                CreateContact(
                    email=address,
                    update_enabled=True,
                    list_ids=[self._list_id],
                )
            )
        except ApiException as e:
            current_app.logger.error(f"Error creating contact: {e}")
            raise ValueError("Error creating contact")

    def _send_welcome_email(self, address: str):
        """
        Send a transactional "welcome" email to the specified address.
        May raise ValueError.

        See https://developers.sendinblue.com/reference/sendtransacemail
        """
        api = TransactionalEmailsApi(self._make_client())
        # Render the email in HTML
        email_html = render_template(
            "email/welcome_email.html",
            # TODO: don't hardcode this URL. Need a global configuration that sets the filename.
            # header_image=url_for('static', filename='site-banner.jpg', _external=True),
            header_url="https://www.stefanonsoftware.com/static/site-banner.JPG",
            recipient=address,
        )
        try:
            api.send_transac_email(
                SendSmtpEmail(
                    to=[{"email": address}],
                    reply_to={
                        "email": "stefan@stefanonsoftware.com",
                        "name": "Stefan Kussmaul",
                    },
                    html_content=email_html,
                    sender={
                        "name": "Stefan Kussmaul",
                        "email": "stefan@stefanonsoftware.com",
                    },
                    subject="Welcome to the StefanOnSoftware Email List!",
                )
            )
        except ApiException as e:
            current_app.logger.error(f"Error sending transactional email: {e}")
            raise ValueError("Error sending welcome email")

    def broadcast_new_post(self, post: Post):
        """
        Creates and sends an email campaign notifying subscribers of
        the new post. May raise ValueError.
        """
        current_app.logger.info(
            f"Broadcasting email campaign for post with slug {post.slug}"
        )
        campaign_id = self._create_campaign(post)
        self._send_campaign(campaign_id)
        current_app.logger.info(
            f"Email campaign has been scheduled for delivery. id={campaign_id}"
        )

    def _create_campaign(self, post: Post) -> int:
        """
        Create a campaign notifying subscribers of the given post.
        Returns the campaign ID. May raise ValueError.

        See https://developers.sendinblue.com/reference/createemailcampaign-1
        """
        api = EmailCampaignsApi(self._make_client())
        email_html = render_template(
            "email/new_post_email.html",
            header_url=post.banner_image.make_url(external=True),
            post=post,
        )
        # Note: here is how you would set the "scheduled_at" time directly in the API call:
        # send_time = datetime.datetime.now(datetime.timezone.utc)
        # CreateEmailCampaign.scheduled_at = send_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z',
        try:
            api_response = api.create_email_campaign(
                CreateEmailCampaign(
                    tag="New Post",
                    sender={
                        "name": "Stefan Kussmaul",
                        "email": "stefan@stefanonsoftware.com",
                    },
                    name=f"New Post - {post.title}",
                    html_content=email_html,
                    subject="A new post from StefanOnSoftware!",
                    reply_to="stefan@stefanonsoftware.com",
                    recipients={"listIds": [self._list_id]},
                )
            )
            current_app.logger.debug(
                f"Email campaign created with id={api_response.id}"
            )
            return api_response.id
        except ApiException as e:
            current_app.logger.error(f"Error creating campaign: {e}")
            raise ValueError("Error creating campaign")

    def _send_campaign(self, campaign_id: int):
        """Send the specified campaign now. May raise ValueError."""
        api = EmailCampaignsApi(self._make_client())
        try:
            api.send_email_campaign_now(campaign_id)
            current_app.logger.debug("Campaign has been sent")
        except ApiException as e:
            current_app.logger.error(f"Error sending campaign: {e}")
            raise ValueError("Error sending campaign")


def get_email_provider() -> EmailProvider:
    """
    Get an instance of EmailProvider for the current thread.

    Throws ValueError if the current app is not configured for sending emails.
    """
    if not current_app.config[ConfigKeys.USE_EMAIL_LIST]:
        raise ValueError("App has not been configured to use the email API")
    if "email_provider" not in g:
        g.email_provider = EmailProvider(
            current_app.config[ConfigKeys.EMAIL_API_KEY],
            current_app.config[ConfigKeys.EMAIL_LIST_ID],
        )
    return g.email_provider
