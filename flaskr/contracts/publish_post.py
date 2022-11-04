import marshmallow as msh
import dataclasses as dc
from typing import Optional, Dict


@dc.dataclass
class PublishPostContract:
    post_id: int
    send_email: bool

    @staticmethod
    def get_schema() -> 'PublishPostSchema':
        return PublishPostSchema()

    @staticmethod
    def from_json(_json: Optional[Dict]) -> 'PublishPostContract':
        return PublishPostContract.get_schema().load(_json if _json else {})


class PublishPostSchema(msh.Schema):
    post_id = msh.fields.Integer(
        required=True,
        allow_none=False,
    )
    send_email = msh.fields.Boolean(
        required=True,
        allow_none=False,
    )

    @msh.post_load
    def make_contract(self, data, **kwargs) -> PublishPostContract:
        return PublishPostContract(**data)
