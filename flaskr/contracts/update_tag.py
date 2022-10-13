import marshmallow as msh
import dataclasses as dc
from marshmallow import validate
from typing import Optional
import flaskr.api.constants as constants


@dc.dataclass
class UpdateTagContract:
    name: str
    description: str
    color: Optional[str] = None

    @staticmethod
    def get_schema() -> 'UpdateTagSchema':
        return UpdateTagSchema()

    @staticmethod
    def from_json(_json: dict) -> 'UpdateTagContract':
        return UpdateTagContract.get_schema().load(_json)


class UpdateTagSchema(msh.Schema):
    name = msh.fields.String(
        required=True,
        allow_none=False,
        data_key='name',
    )
    description = msh.fields.String(
        required=True,
        allow_none=False,
        data_key='description',
    )
    color = msh.fields.String(
        required=False,
        load_default=None,
        data_key='color',
        validate=validate.Regexp(constants.COLOR_REGEX),
    )

    @msh.post_load
    def make_contract(self, data, **kwargs) -> UpdateTagContract:
        return UpdateTagContract(**data)
