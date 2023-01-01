import marshmallow as msh
import dataclasses as dc
from typing import Optional, Dict


@dc.dataclass
class GetPostsContract:
    is_featured: Optional[bool] = None
    is_published: Optional[bool] = None
    limit: Optional[int] = None
    offset: Optional[int] = None

    @staticmethod
    def get_schema() -> 'GetPostsSchema':
        return GetPostsSchema()

    @staticmethod
    def from_json(_json: Optional[Dict]) -> 'GetPostsContract':
        return GetPostsContract.get_schema().load(_json if _json else {})


class GetPostsSchema(msh.Schema):
    is_featured = msh.fields.Boolean()
    is_published = msh.fields.Boolean()
    limit = msh.fields.Integer()
    offset = msh.fields.Integer()

    @msh.post_load
    def make_contract(self, data, **kwargs) -> GetPostsContract:
        return GetPostsContract(**data)
