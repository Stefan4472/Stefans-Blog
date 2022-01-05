import datetime as dt
import marshmallow as msh
import dataclasses as dc
import typing
import flaskr.api.constants as constants


@dc.dataclass
class CreatePostContract:
    slug: str
    title: str
    byline: typing.Optional[str]
    date: typing.Optional[dt.datetime]
    image: str
    thumbnail: str
    banner: str
    tags: typing.Optional[typing.List[str]]
    publish: typing.Optional[bool]
    feature: typing.Optional[bool]
    title_color: typing.Optional[str]

    @staticmethod
    def get_schema() -> 'CreatePostSchema':
        return CreatePostSchema()

    @staticmethod
    def from_json(_json: dict) -> 'CreatePostContract':
        return CreatePostContract.get_schema().load(_json)


class CreatePostSchema(msh.Schema):
    slug = msh.fields.String(
        required=True,
        allow_none=False,
        data_key=constants.KEY_SLUG,
    )
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
    date = msh.fields.Date(
        required=False,
        load_default=None,
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

    class Meta:
        dateformat = constants.DATE_FORMAT

    @msh.post_load
    def make_contract(self, data, **kwargs) -> CreatePostContract:
        return CreatePostContract(**data)