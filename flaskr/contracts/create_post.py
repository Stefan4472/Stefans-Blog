import marshmallow as msh
import dataclasses as dc
from marshmallow import validate
from typing import Optional, Dict
import flaskr.api.constants as constants


@dc.dataclass
class CreatePostContract:
    slug: str = None
    title: str = None
    byline: str = None
    featured_image: str = None
    banner_image: str = None
    thumbnail_image: str = None

    @staticmethod
    def get_schema() -> 'CreatePostSchema':
        return CreatePostSchema()

    @staticmethod
    def from_json(_json: Optional[Dict]) -> 'CreatePostContract':
        return CreatePostContract.get_schema().load(_json if _json else {})


class CreatePostSchema(msh.Schema):
    slug = msh.fields.String(validate=msh.validate.Regexp(constants.SLUG_REGEX))
    title = msh.fields.String()
    byline = msh.fields.String()
    featured_image = msh.fields.String()
    banner_image = msh.fields.String()
    thumbnail_image = msh.fields.String()

    @msh.post_load
    def make_contract(self, data, **kwargs) -> CreatePostContract:
        return CreatePostContract(**data)
