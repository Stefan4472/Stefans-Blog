import datetime as dt
import marshmallow as msh
import dataclasses as dc
import typing
import flaskr.api.constants as constants


@dc.dataclass
class PatchPostContract:
    """
    Note: basically the same as `CreatePostContract` except all fields
    are optional and there is no `slug`.
    """
    title: typing.Optional[str] = None
    byline: typing.Optional[str] = None
    publish_date: typing.Optional[dt.datetime] = None
    image: typing.Optional[str] = None
    thumbnail: typing.Optional[str] = None
    banner: typing.Optional[str] = None
    tags: typing.Optional[typing.List[str]] = None
    publish: typing.Optional[bool] = None
    feature: typing.Optional[bool] = None
    title_color: typing.Optional[str] = None

    @staticmethod
    def get_schema() -> 'PatchPostSchema':
        return PatchPostSchema()

    @staticmethod
    def from_json(_json: dict) -> 'PatchPostContract':
        return PatchPostContract.get_schema().load(_json)


class PatchPostSchema(msh.Schema):
    title = msh.fields.String(data_key=constants.KEY_TITLE)
    byline = msh.fields.String(data_key=constants.KEY_BYLINE)
    publish_date = msh.fields.DateTime(
        format=constants.DATE_FORMAT,
        data_key=constants.KEY_DATE,
    )
    image = msh.fields.String(data_key=constants.KEY_IMAGE)
    thumbnail = msh.fields.String(data_key=constants.KEY_THUMBNAIL)
    banner = msh.fields.String(data_key=constants.KEY_BANNER)
    tags = msh.fields.List(
        msh.fields.String(),
        data_key=constants.KEY_TAGS,
    )
    publish = msh.fields.Boolean(data_key=constants.KEY_PUBLISH)
    feature = msh.fields.Boolean(data_key=constants.KEY_FEATURE)
    title_color = msh.fields.String(
        data_key=constants.KEY_TITLE_COLOR,
        validate=msh.validate.Regexp(constants.COLOR_REGEX),
    )

    @msh.post_load
    def make_contract(self, data, **kwargs) -> PatchPostContract:
        return PatchPostContract(**data)
