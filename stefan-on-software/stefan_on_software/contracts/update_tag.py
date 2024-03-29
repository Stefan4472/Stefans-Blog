import dataclasses as dc
from typing import Dict, Optional

import marshmallow as msh
import stefan_on_software.contracts.constants as constants
from marshmallow import validate


@dc.dataclass
class UpdateTagContract:
    name: str
    description: str
    color: Optional[str] = None

    @staticmethod
    def get_schema() -> "UpdateTagSchema":
        return UpdateTagSchema()

    @staticmethod
    def from_json(_json: Optional[Dict]) -> "UpdateTagContract":
        return UpdateTagContract.get_schema().load(_json if _json else {})


class UpdateTagSchema(msh.Schema):
    name = msh.fields.String(
        required=True,
        allow_none=False,
        data_key="name",
    )
    description = msh.fields.String(
        required=True,
        allow_none=False,
        data_key="description",
    )
    color = msh.fields.String(
        required=False,
        load_default=None,
        data_key="color",
        validate=validate.Regexp(constants.COLOR_REGEX),
    )

    @msh.post_load
    def make_contract(self, data, **kwargs) -> UpdateTagContract:
        return UpdateTagContract(**data)
