import datetime as dt
import marshmallow as msh
import dataclasses as dc
from typing import Optional, Dict, List
import flaskr.api.constants as constants


@dc.dataclass
class UpdatePostContract:
    """Note: basically the same as `CreatePostContract`, but without `slug`"""
    title: str
    byline: Optional[str]
    publish_date: Optional[dt.datetime]
    image: str
    thumbnail: str
    banner: str
    tags: Optional[List[str]]
    publish: Optional[bool]
    feature: Optional[bool]
    title_color: Optional[str]

    @staticmethod
    def get_schema() -> 'UpdatePostSchema':
        return UpdatePostSchema()

    @staticmethod
    def from_json(_json: Optional[Dict]) -> 'UpdatePostContract':
        return UpdatePostContract.get_schema().load(_json if _json else {})


class UpdatePostSchema(msh.Schema):
    title = msh.fields.String(
        required=True,
        allow_none=False,
        data_key=constants.KEY_TITLE,
    )
    byline = msh.fields.String(
        required=False,
        load_default=None,
        data_key=constants.KEY_BYLINE,
    )
    publish_date = msh.fields.DateTime(
        required=False,
        load_default=None,
        format=constants.DATE_FORMAT,
        data_key=constants.KEY_DATE,
    )
    image = msh.fields.String(
        required=True,
        allow_none=False,
        data_key=constants.KEY_IMAGE,
    )
    thumbnail = msh.fields.String(
        required=True,
        allow_none=False,
        data_key=constants.KEY_THUMBNAIL,
    )
    banner = msh.fields.String(
        required=True,
        allow_none=False,
        data_key=constants.KEY_BANNER,
    )
    tags = msh.fields.List(
        msh.fields.String(),
        required=False,
        load_default=None,
        data_key=constants.KEY_TAGS,
    )
    publish = msh.fields.Boolean(
        required=False,
        load_default=None,
        data_key=constants.KEY_PUBLISH,
    )
    feature = msh.fields.Boolean(
        required=False,
        load_default=None,
        data_key=constants.KEY_FEATURE,
    )
    title_color = msh.fields.String(
        required=False,
        load_default=None,
        data_key=constants.KEY_TITLE_COLOR,
        validate=msh.validate.Regexp(constants.COLOR_REGEX),
    )

    @msh.post_load
    def make_contract(self, data, **kwargs) -> UpdatePostContract:
        return UpdatePostContract(**data)
