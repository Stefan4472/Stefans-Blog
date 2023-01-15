import dataclasses as dc
from typing import Dict, Optional

import marshmallow as msh
from marshmallow import validate

import flaskr.contracts.constants as constants


@dc.dataclass
class UpdatePostContract:
    slug: str
    title: str
    byline: str
    featured_image: Optional[str]
    banner_image: Optional[str]
    thumbnail_image: Optional[str]

    @staticmethod
    def get_schema() -> "UpdatePostSchema":
        return UpdatePostSchema()

    @staticmethod
    def from_json(_json: Optional[Dict]) -> "UpdatePostContract":
        return UpdatePostContract.get_schema().load(_json if _json else {})


class UpdatePostSchema(msh.Schema):
    slug = msh.fields.String(
        required=True,
        allow_none=False,
        validate=msh.validate.Regexp(constants.SLUG_REGEX),
    )
    title = msh.fields.String(
        required=True,
        allow_none=False,
    )
    byline = msh.fields.String(
        required=True,
        allow_none=False,
    )
    featured_image = msh.fields.String(
        required=True,
        allow_none=True,
    )
    banner_image = msh.fields.String(
        required=True,
        allow_none=True,
    )
    thumbnail_image = msh.fields.String(
        required=True,
        allow_none=True,
    )

    @msh.post_load
    def make_contract(self, data, **kwargs) -> UpdatePostContract:
        return UpdatePostContract(**data)
