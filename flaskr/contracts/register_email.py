import marshmallow as msh
import dataclasses as dc
from typing import Optional, Dict

@dc.dataclass
class RegisterEmailContract:
    address: str

    @staticmethod
    def get_schema() -> 'RegisterEmailSchema':
        return RegisterEmailSchema()

    @staticmethod
    def from_json(_json: Optional[Dict]) -> 'RegisterEmailContract':
        return RegisterEmailContract.get_schema().load(_json if _json else {})


class RegisterEmailSchema(msh.Schema):
    address = msh.fields.Email(
        required=True,
        allow_none=False,
    )

    @msh.post_load
    def make_contract(self, data, **kwargs) -> RegisterEmailContract:
        return RegisterEmailContract(**data)
