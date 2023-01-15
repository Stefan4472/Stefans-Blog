import dataclasses as dc
from typing import Dict, Optional

import marshmallow as msh
from marshmallow import validate

import flaskr.contracts.constants as constants


@dc.dataclass
class CreatePostContract:
    slug: Optional[str] = None
    title: Optional[str] = None
    byline: Optional[str] = None
    featured_image: Optional[str] = None
    banner_image: Optional[str] = None
    thumbnail_image: Optional[str] = None

    @staticmethod
    def get_schema() -> "CreatePostSchema":
        return CreatePostSchema()

    @staticmethod
    def from_json(_json: Optional[Dict]) -> "CreatePostContract":
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
