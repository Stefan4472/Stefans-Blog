import os
import typing
import pathlib
import dataclasses as dc


# TODO: REMOVE FEATURED_POSTS_PATH
# TODO: ADD KEYS FOR REMOTE UPLOAD
@dc.dataclass
class Config:
    DATABASE_PATH: pathlib.Path
    LOG_PATH: pathlib.Path
    FEATURED_POSTS_PATH: pathlib.Path
    SEARCH_INDEX_PATH: pathlib.Path
    MANIFEST_PATH: pathlib.Path
    TRAFFIC_API: typing.Optional[str] = None
    TRAFFIC_KEY: typing.Optional[str] = None
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + r'C:\Users\stefa\Downloads\app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def get_env_path(key: str) -> typing.Optional[pathlib.Path]:
        return pathlib.Path(os.environ.get(key)) if os.environ.get(key) else None

    @staticmethod
    def load_from_env(instance_path: pathlib.Path) -> 'Config':
        return Config(
            Config.get_env_path('DATABASE_PATH') or instance_path / 'posts.db',
            Config.get_env_path('LOG_PATH') or instance_path / 'sitelog.txt',
            Config.get_env_path('FEATURED_POSTS_PATH') or instance_path / 'featured_posts.txt',
            Config.get_env_path('SEARCH_INDEX_PATH') or instance_path / 'index.json',
            Config.get_env_path('MANIFEST_PATH') or instance_path / 'manifest.json',
            TRAFFIC_API=os.environ.get('TRAFFIC_API'),
            TRAFFIC_KEY=os.environ.get('TRAFFIC_KEY'),
        )
