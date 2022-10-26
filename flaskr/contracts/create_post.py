import marshmallow as msh
import dataclasses as dc
from typing import Optional, Dict
import flaskr.api.constants as constants


@dc.dataclass
class CreatePostContract:
    slug: str = None
    title: str = None
    byline: str = None
    featured_file_id: str = None
    banner_file_id: str = None
    thumbnail_file_id: str = None

    @staticmethod
    def get_schema() -> 'CreatePostSchema':
        return CreatePostSchema()

    @staticmethod
    def from_json(_json: Optional[Dict]) -> 'CreatePostContract':
        return CreatePostContract.get_schema().load(_json if _json else {})


class CreatePostSchema(msh.Schema):
    slug = msh.fields.String(data_key=constants.KEY_SLUG)
    title = msh.fields.String(data_key=constants.KEY_TITLE)
    byline = msh.fields.String(data_key=constants.KEY_BYLINE)
    featured_image = msh.fields.String(data_key=constants.KEY_IMAGE)
    banner_image = msh.fields.String(data_key=constants.KEY_BANNER)
    thumbnail_image = msh.fields.String(data_key=constants.KEY_THUMBNAIL)

    @msh.post_load
    def make_contract(self, data, **kwargs) -> CreatePostContract:
        return CreatePostContract(**data)
