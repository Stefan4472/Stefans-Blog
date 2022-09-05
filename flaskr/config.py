import os
import typing
import dataclasses as dc
from pathlib import Path
from enum import Enum
from typing import Dict


class Keys(Enum):
    """Keys used to reference config values."""
    SECRET_KEY = 'SECRET_KEY'
    SQLALCHEMY_DATABASE_URI = 'SQLALCHEMY_DATABASE_URI'
    TRAFFIC_LOG_PATH = 'TRAFFIC_LOG_PATH'
    SEARCH_INDEX_PATH = 'SEARCH_INDEX_PATH'
    USE_SITE_ANALYTICS = 'USE_SITE_ANALYTICS'
    USE_EMAIL_LIST = 'USE_EMAIL_LIST'
    TRAFFIC_API = 'TRAFFIC_API'
    TRAFFIC_KEY = 'TRAFFIC_KEY'
    EMAIL_KEY = 'EMAIL_KEY'
    EMAIL_LIST_ID = 'EMAIL_LIST_ID'
    SQLALCHEMY_TRACK_MODIFICATIONS = 'SQLALCHEMY_TRACK_MODIFICATIONS'
    PAGINATE_POSTS_PER_PAGE = 'PAGINATE_POSTS_PER_PAGE'


@dc.dataclass
class Config:
    """Stores configuration variables for the Flask app."""
    # TODO: provide instance path as a config variable?
    # App secret key
    secret_key: str
    # URI used by SQLAlchemy to connect to the database.
    # Note: for SQLite, URI must start with `sqlite:///`, e.g. `sqlite:///instance/db.sqlite`
    sql_alchemy_database_uri: str
    # Path to the file where web traffic should be logged
    traffic_log_path: Path
    # Path to the serialized search index file TODO: make optional(?)
    search_index_path: Path

    # Whether to use the SiteAnalytics API
    use_site_analytics: bool = False
    # Whether to provide an email list via Sendinblue
    use_email_list: bool = False

    # Settings for the site-analytics API. Only relevant if USE_SITE_ANALYTICS = true
    traffic_api: typing.Optional[str] = None
    traffic_key: typing.Optional[str] = None

    # Settings for Email List. Only relevant if USE_EMAIL_LIST = true
    # API Key for Sendinblue
    email_key: typing.Optional[str] = None
    # ID of the email list to use
    email_list_id: typing.Optional[int] = None

    # SQLAlchemy setting: whether to track modifications
    sql_alchemy_track_modifications: bool = False
    # Number of posts to show per page in results (used for pagination)
    paginate_posts_per_page = 8

    def check_validity(self):
        """Run checks to ensure """
        if not self.secret_key:
            raise ValueError(f'{Keys.SECRET_KEY} is unset')
        if self.use_email_list and not (self.email_key and self.email_list_id):
            raise ValueError(f'{Keys.USE_EMAIL_LIST} = True but {Keys.EMAIL_KEY} and {Keys.EMAIL_LIST_ID} are not both configured')
        if self.use_site_analytics and not (self.traffic_key and self.traffic_api):
            raise ValueError(f'{Keys.USE_SITE_ANALYTICS} = True but {Keys.TRAFFIC_KEY} and {Keys.TRAFFIC_API} are not both configured')

    def to_dict(self) -> Dict:
        return {
            Keys.SECRET_KEY: self.secret_key,
            Keys.SQLALCHEMY_DATABASE_URI: self.sql_alchemy_database_uri,
            Keys.TRAFFIC_LOG_PATH: self.traffic_log_path,
            Keys.SEARCH_INDEX_PATH: self.search_index_path,
            Keys.USE_SITE_ANALYTICS: self.use_site_analytics,
            Keys.USE_EMAIL_LIST: self.use_email_list,
            Keys.TRAFFIC_API: self.traffic_api,
            Keys.TRAFFIC_KEY: self.traffic_key,
            Keys.EMAIL_KEY: self.email_key,
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
        optional = [Keys.USE_SITE_ANALYTICS, Keys.USE_EMAIL_LIST, Keys.TRAFFIC_API, Keys.TRAFFIC_KEY, Keys.EMAIL_KEY,
                    Keys.EMAIL_LIST_ID, Keys.SQLALCHEMY_TRACK_MODIFICATIONS, Keys.PAGINATE_POSTS_PER_PAGE]
        kwargs = {key: os.environ[key] for key in optional if key in os.environ}

        return Config(
            os.environ[Keys.SECRET_KEY],
            os.environ[Keys.SQLALCHEMY_DATABASE_URI],
            Path(os.environ[Keys.TRAFFIC_LOG_PATH]),
            Path(os.environ[Keys.SEARCH_INDEX_PATH]),
            **kwargs,
        )

        # if Keys.USE_SITE_ANALYTICS in os.environ:
        #     config.USE_SITE_ANALYTICS = os.environ[Keys.USE_SITE_ANALYTICS]
        # if Keys.USE_EMAIL_LIST in os.environ:
        #     config.USE_EMAIL_LIST = os.environ[Keys.USE_EMAIL_LIST]
        # if Keys.TRAFFIC_API in os.environ:
        #     config.TRAFFIC_API = os.environ[Keys.TRAFFIC_API]
        # if Keys.TRAFFIC_KEY in os.environ:
        #     config.TRAFFIC_KEY = os.environ[Keys.TRAFFIC_KEY]
        # if Keys.EMAIL_KEY in os.environ:
        #     config.EMAIL_KEY = os.environ[Keys.EMAIL_KEY]
        # if Keys.EMAIL_LIST_ID in os.environ:
        #     config.EMAIL_LIST_ID = os.environ[Keys.EMAIL_LIST_ID]
        # if Keys.SQLALCHEMY_TRACK_MODIFICATIONS in os.environ:
        #     config.SQLALCHEMY_TRACK_MODIFICATIONS = os.environ[Keys.SQLALCHEMY_TRACK_MODIFICATIONS]
        # if Keys.PAGINATE_POSTS_PER_PAGE in os.environ:
        #     config.PAGINATE_POSTS_PER_PAGE = os.environ[Keys.PAGINATE_POSTS_PER_PAGE]
        #
        # return config
