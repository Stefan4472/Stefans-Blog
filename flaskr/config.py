import os
import typing
import dataclasses as dc
from pathlib import Path
from typing import Dict


class Keys:
    """
    Strings used to reference config values.

    Use the string values when setting environment variables
    or when accessing `flask.current_app.config`.
    """
    SECRET_KEY = 'SECRET_KEY'
    SQLALCHEMY_DATABASE_URI = 'SQLALCHEMY_DATABASE_URI'
    TRAFFIC_LOG_PATH = 'TRAFFIC_LOG_PATH'
    SEARCH_INDEX_PATH = 'SEARCH_INDEX_PATH'
    USE_SITE_ANALYTICS = 'USE_SITE_ANALYTICS'
    SITE_ANALYTICS_URL = 'SITE_ANALYTICS_URL'
    SITE_ANALYTICS_KEY = 'SITE_ANALYTICS_KEY'
    USE_EMAIL_LIST = 'USE_EMAIL_LIST'
    EMAIL_API_KEY = 'EMAIL_API_KEY'
    EMAIL_LIST_ID = 'EMAIL_LIST_ID'
    SQLALCHEMY_TRACK_MODIFICATIONS = 'SQLALCHEMY_TRACK_MODIFICATIONS'
    PAGINATE_POSTS_PER_PAGE = 'PAGINATE_POSTS_PER_PAGE'


@dc.dataclass
class Config:
    """
    Stores configuration variables for the Flask app.

    Use `to_dict()` when populating `flask.current_app.config`. This
    will ensure that the keys are properly set.

    Can be used to read from environment variables using `load_from_env()`.
    """
    # App secret key
    secret_key: str
    # URI used by SQLAlchemy to connect to the database.
    # Note: for SQLite, URI must start with `sqlite:///`
    sql_alchemy_database_uri: str
    # Path to the file where web traffic should be logged
    traffic_log_path: Path
    # Path to the serialized search index file TODO: make optional(?)
    search_index_path: Path

    # Whether to use the SiteAnalytics API
    use_site_analytics: bool = False
    # Whether to provide an email list via Sendinblue
    use_email_list: bool = False

    # Settings for the Site-Analytics API. Only relevant if use_site_analytics = true
    site_analytics_url: typing.Optional[str] = None
    site_analytics_key: typing.Optional[str] = None

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
            raise ValueError(f'{Keys.SECRET_KEY} is unset')
        if self.use_email_list and not (self.email_api_key and self.email_list_id):
            raise ValueError(f'{Keys.USE_EMAIL_LIST} = True but {Keys.EMAIL_API_KEY} and {Keys.EMAIL_LIST_ID} are not both configured')
        if self.use_site_analytics and not (self.site_analytics_key and self.site_analytics_url):
            raise ValueError(f'{Keys.USE_SITE_ANALYTICS} = True but {Keys.SITE_ANALYTICS_KEY} and {Keys.SITE_ANALYTICS_URL} are not both configured')

    def to_dict(self) -> Dict:
        """Return parameters as a dictionary."""
        return {
            Keys.SECRET_KEY: self.secret_key,
            Keys.SQLALCHEMY_DATABASE_URI: self.sql_alchemy_database_uri,
            Keys.TRAFFIC_LOG_PATH: self.traffic_log_path,
            Keys.SEARCH_INDEX_PATH: self.search_index_path,
            Keys.USE_SITE_ANALYTICS: self.use_site_analytics,
            Keys.USE_EMAIL_LIST: self.use_email_list,
            Keys.SITE_ANALYTICS_URL: self.site_analytics_url,
            Keys.SITE_ANALYTICS_KEY: self.site_analytics_key,
            Keys.EMAIL_API_KEY: self.email_api_key,
            Keys.EMAIL_LIST_ID: self.email_list_id,
            Keys.SQLALCHEMY_TRACK_MODIFICATIONS: self.sql_alchemy_track_modifications,
            Keys.PAGINATE_POSTS_PER_PAGE: self.paginate_posts_per_page,
        }

    @staticmethod
    def load_from_env() -> 'Config':
        """Load config from environment variables."""
        if Keys.SECRET_KEY not in os.environ:
            raise ValueError(f'{Keys.SECRET_KEY} is not declared')
        if Keys.SQLALCHEMY_DATABASE_URI not in os.environ:
            raise ValueError(f'{Keys.SQLALCHEMY_DATABASE_URI} is not declared')
        if Keys.TRAFFIC_LOG_PATH not in os.environ:
            raise ValueError(f'{Keys.TRAFFIC_LOG_PATH} is not declared')
        if Keys.SEARCH_INDEX_PATH not in os.environ:
            raise ValueError(f'{Keys.SEARCH_INDEX_PATH} is not declared')

        # Collect optional settings
        optional = [
            Keys.USE_SITE_ANALYTICS, Keys.USE_EMAIL_LIST, Keys.SITE_ANALYTICS_URL,
            Keys.SITE_ANALYTICS_KEY, Keys.EMAIL_API_KEY, Keys.EMAIL_LIST_ID,
            Keys.SQLALCHEMY_TRACK_MODIFICATIONS, Keys.PAGINATE_POSTS_PER_PAGE,
        ]
        kwargs = {key: os.environ[key] for key in optional if key in os.environ}

        return Config(
            os.environ[Keys.SECRET_KEY],
            os.environ[Keys.SQLALCHEMY_DATABASE_URI],
            Path(os.environ[Keys.TRAFFIC_LOG_PATH]),
            Path(os.environ[Keys.SEARCH_INDEX_PATH]),
            **kwargs,
        )
