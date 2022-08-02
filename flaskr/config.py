import os
import typing
import pathlib
import dataclasses as dc


@dc.dataclass
class Config:
    DATABASE_PATH: pathlib.Path
    LOG_PATH: pathlib.Path
    SEARCH_INDEX_PATH: pathlib.Path
    # Our secret key (required for external API access)
    SECRET_KEY: str
    # Settings for site-analytics API
    TRAFFIC_API: typing.Optional[str] = None
    TRAFFIC_KEY: typing.Optional[str] = None
    # Settings for Email List, currently only supporting SendInBlue
    # API Key
    EMAIL_KEY: typing.Optional[str] = None
    # List ID
    EMAIL_LIST_ID: typing.Optional[int] = None
    # Note: for SQLite, URI must start with `sqlite:///`
    SQLALCHEMY_DATABASE_URI: str = 'sqlite:///'
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    # Number of posts to show per page (used for pagination)
    PAGINATE_POSTS_PER_PAGE = 8

    @staticmethod
    def get_env_path(key: str) -> typing.Optional[pathlib.Path]:
        return pathlib.Path(os.environ.get(key)) if os.environ.get(key) else None

    @staticmethod
    def load_from_env(instance_path: pathlib.Path) -> 'Config':
        db_path = Config.get_env_path('DATABASE_PATH') or instance_path / 'posts.db'
        return Config(
            db_path,
            Config.get_env_path('LOG_PATH') or instance_path / 'sitelog.txt',
            Config.get_env_path('SEARCH_INDEX_PATH') or instance_path / 'index.json',
            Config.get_env_path('SECRET_KEY') or '',
            TRAFFIC_API=os.environ.get('TRAFFIC_API') or '',
            TRAFFIC_KEY=os.environ.get('TRAFFIC_KEY') or '',
            EMAIL_KEY=os.environ.get('EMAIL_KEY') or '',
            EMAIL_LIST_ID=int(os.environ.get('EMAIL_LIST_ID')) or None,
            SQLALCHEMY_DATABASE_URI='sqlite:///' + str(db_path),
        )
