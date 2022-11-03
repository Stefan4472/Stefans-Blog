"""Contract to add a tag to a post."""
import marshmallow as msh
import dataclasses as dc
from typing import Optional, Dict


@dc.dataclass
class AddTagContract:
    tag: str

    @staticmethod
    def get_schema() -> 'AddTagSchema':
        return AddTagSchema()

    @staticmethod
    def from_json(_json: Optional[Dict]) -> 'AddTagContract':
        return AddTagContract.get_schema().load(_json if _json else {})


class AddTagSchema(msh.Schema):
    tag = msh.fields.String(
        required=True,
        allow_none=False,
    )

    @msh.post_load
    def make_contract(self, data, **kwargs) -> AddTagContract:
        return AddTagContract(**data)
