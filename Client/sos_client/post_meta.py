import json
import typing
import marshmallow as msh
import dataclasses as dc
from typing import Optional, List
from pathlib import Path
from datetime import datetime, date
from sos_client import constants


@dc.dataclass
class PostMeta:
    """Store post configuration ("post-meta") data."""
    slug: Optional[str] = None
    title: Optional[str] = None
    byline: Optional[str] = None
    date: Optional[date] = None
    tags: Optional[List[str]] = None
    # TODO: would be good to support Path objects
    image: Optional[str] = None
    banner: Optional[str] = None
    thumbnail: Optional[str] = None

    @staticmethod
    def parse_from_file(filepath: Path) -> 'PostMeta':
        """Parse a `post-meta.json` file and return an instance of `PostConfig`."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='strict') as f:
                cfg_json = json.load(f)
            return PostMetaSchema().load(cfg_json)
        except IOError:
            raise ValueError(f'Could not open the config file at ("{filepath.absolute()}")')
        except json.JSONDecodeError as e:
            raise ValueError(f'Invalid JSON in the provided config file: {e}')
        except msh.exceptions.ValidationError as e:
            raise ValueError(f'Invalid post-meta.json file: {e}')

    def write_to_file(self, filepath: Path):
        """Write `PostConfig` instance out to specified filepath."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(PostMetaSchema().dump(self), f, indent=4, sort_keys=True)


class PostMetaSchema(msh.Schema):
    slug = msh.fields.String(validate=msh.validate.Regexp(constants.SLUG_REGEX))
    title = msh.fields.String()
    byline = msh.fields.String()
    date = msh.fields.Date(format=constants.DATE_FORMAT)
    tags = msh.fields.List(msh.fields.String(data_key='tags', validate=msh.validate.Regexp(constants.SLUG_REGEX)))
    image = msh.fields.String()
    banner = msh.fields.String()
    thumbnail = msh.fields.String()

    @msh.post_load
    def make_meta(self, data, **kwargs) -> PostMeta:
        return PostMeta(**data)
