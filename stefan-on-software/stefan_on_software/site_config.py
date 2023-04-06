import dataclasses as dc
import os
import typing
from typing import Dict


class ConfigKeys:
    """
    Strings used to reference config values.

    Use the string values when setting environment variables
    or when accessing `flask.current_app.config`.
    """

    SECRET_KEY = "SECRET_KEY"
    SQLALCHEMY_DATABASE_URI = "SQLALCHEMY_DATABASE_URI"
    TRAFFIC_LOG_PATH = "TRAFFIC_LOG_PATH"
    SEARCH_INDEX_PATH = "SEARCH_INDEX_PATH"
    INSTANCE_PATH = "INSTANCE_PATH"
    STATIC_PATH = "STATIC_PATH"
    TESTING = "TESTING"
    USE_SITE_ANALYTICS = "USE_SITE_ANALYTICS"
    SITE_ANALYTICS_URL = "SITE_ANALYTICS_URL"
    SITE_ANALYTICS_KEY = "SITE_ANALYTICS_KEY"
    USE_EMAIL_LIST = "USE_EMAIL_LIST"
    EMAIL_API_KEY = "EMAIL_API_KEY"
    EMAIL_LIST_ID = "EMAIL_LIST_ID"
    SQLALCHEMY_TRACK_MODIFICATIONS = "SQLALCHEMY_TRACK_MODIFICATIONS"
    PAGINATE_POSTS_PER_PAGE = "PAGINATE_POSTS_PER_PAGE"
    SITEMAP_PATH = "SITEMAP_PATH"


@dc.dataclass
class SiteConfig:
    """
    Stores configuration variables for the Flask app.

    Create a dictionary with configured values via `to_dict()`.
    Init a SiteConfig instance from environment variables via `load_from_env()`.
    """

    # App secret key
    secret_key: str
    # Path to the instance folder RELATIVE TO APP ROOT.
    # Must not start with "/", which would lead to it being
    # interpreted as an absolute path. Example: "test-instance"
    rel_instance_path: str = None
    # Path to the static folder RELATIVE TO APP ROOT.
    # Must not start with "/". Example: "test-static"
    rel_static_path: str = None

    # Whether to run the app in "testing" mode
    # https://flask.palletsprojects.com/en/2.2.x/config/#TESTING
    testing: bool = False

    # Whether to use the SiteAnalytics API
    use_site_analytics: bool = False
    # Settings for the Site-Analytics API. Only relevant if use_site_analytics = true
    site_analytics_url: typing.Optional[str] = None
    site_analytics_key: typing.Optional[str] = None

    # Whether to provide an email list via Sendinblue
    use_email_list: bool = False
    # Settings for Email List. Only relevant if use_email_list = true
    # API Key for Sendinblue
    email_api_key: typing.Optional[str] = None
    # ID of the email list to use
    email_list_id: typing.Optional[int] = None

    # SQLAlchemy setting: whether to track modifications
    sql_alchemy_track_modifications: bool = False
    # Number of posts to show per page in results (used for pagination)
    paginate_posts_per_page = 8

    def check_validity(self):
        """
        Run basic checks to ensure there are no obvious problems in the config.
        Raises ValueError in case of a problem.
        """
        if not self.secret_key:
            raise ValueError(f"{ConfigKeys.SECRET_KEY} is unset")
        if self.use_email_list and not (self.email_api_key and self.email_list_id):
            raise ValueError(
                f"{ConfigKeys.USE_EMAIL_LIST} = True but {ConfigKeys.EMAIL_API_KEY} and {ConfigKeys.EMAIL_LIST_ID} are not both configured"
            )
        if self.use_site_analytics and not (
            self.site_analytics_key and self.site_analytics_url
        ):
            raise ValueError(
                f"{ConfigKeys.USE_SITE_ANALYTICS} = True but {ConfigKeys.SITE_ANALYTICS_KEY} and {ConfigKeys.SITE_ANALYTICS_URL} are not both configured"
            )
        if self.rel_instance_path and self.rel_instance_path.startswith("/"):
            raise ValueError(f'{ConfigKeys.INSTANCE_PATH} must not start with "/"')
        if self.rel_static_path and self.rel_static_path.startswith("/"):
            raise ValueError(f'{ConfigKeys.STATIC_PATH} must not start with "/"')

    def to_dict(self) -> Dict:
        """Return parameters as a dictionary."""
        return {
            ConfigKeys.SECRET_KEY: self.secret_key,
            ConfigKeys.INSTANCE_PATH: self.rel_instance_path,
            ConfigKeys.STATIC_PATH: self.rel_static_path,
            ConfigKeys.TESTING: self.testing,
            ConfigKeys.USE_SITE_ANALYTICS: self.use_site_analytics,
            ConfigKeys.USE_EMAIL_LIST: self.use_email_list,
            ConfigKeys.SITE_ANALYTICS_URL: self.site_analytics_url,
            ConfigKeys.SITE_ANALYTICS_KEY: self.site_analytics_key,
            ConfigKeys.EMAIL_API_KEY: self.email_api_key,
            ConfigKeys.EMAIL_LIST_ID: self.email_list_id,
            ConfigKeys.SQLALCHEMY_TRACK_MODIFICATIONS: self.sql_alchemy_track_modifications,
            ConfigKeys.PAGINATE_POSTS_PER_PAGE: self.paginate_posts_per_page,
        }

    @staticmethod
    def load_from_env() -> "SiteConfig":
        """Load config from environment variables."""
        if ConfigKeys.SECRET_KEY not in os.environ:
            raise ValueError(f"{ConfigKeys.SECRET_KEY} is not declared")

        # Collect optional settings
        kwargs = {}
        if ConfigKeys.INSTANCE_PATH in os.environ:
            kwargs["rel_instance_path"] = os.environ[ConfigKeys.INSTANCE_PATH]
        if ConfigKeys.STATIC_PATH in os.environ:
            kwargs["rel_static_path"] = os.environ[ConfigKeys.STATIC_PATH]
        if ConfigKeys.TESTING in os.environ:
            kwargs["testing"] = os.environ[ConfigKeys.TESTING]
        if ConfigKeys.USE_SITE_ANALYTICS in os.environ:
            kwargs["use_site_analytics"] = os.environ[ConfigKeys.USE_SITE_ANALYTICS]
        if ConfigKeys.SITE_ANALYTICS_URL in os.environ:
            kwargs["site_analytics_url"] = os.environ[ConfigKeys.SITE_ANALYTICS_URL]
        if ConfigKeys.SITE_ANALYTICS_KEY in os.environ:
            kwargs["site_analytics_url"] = os.environ[ConfigKeys.SITE_ANALYTICS_KEY]
        if ConfigKeys.USE_EMAIL_LIST in os.environ:
            kwargs["use_email_list"] = os.environ[ConfigKeys.USE_EMAIL_LIST]
        if ConfigKeys.EMAIL_API_KEY in os.environ:
            kwargs["email_api_key"] = os.environ[ConfigKeys.EMAIL_API_KEY]
        if ConfigKeys.EMAIL_LIST_ID in os.environ:
            kwargs["email_list_id"] = os.environ[ConfigKeys.EMAIL_LIST_ID]
        if ConfigKeys.SQLALCHEMY_TRACK_MODIFICATIONS in os.environ:
            kwargs["sql_alchemy_track_modifications"] = os.environ[
                ConfigKeys.SQLALCHEMY_TRACK_MODIFICATIONS
            ]
        if ConfigKeys.PAGINATE_POSTS_PER_PAGE in os.environ:
            kwargs["paginate_posts_per_page"] = os.environ[
                ConfigKeys.PAGINATE_POSTS_PER_PAGE
            ]

        return SiteConfig(os.environ[ConfigKeys.SECRET_KEY], **kwargs)
