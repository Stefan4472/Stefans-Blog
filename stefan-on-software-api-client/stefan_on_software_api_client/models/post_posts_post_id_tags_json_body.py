from typing import Any, Dict, List, Type, TypeVar

import attr

T = TypeVar("T", bound="PostPostsPostIdTagsJsonBody")


@attr.s(auto_attribs=True)
class PostPostsPostIdTagsJsonBody:
    """
    Attributes:
        tag (str): Slug of the tag to add to the post
    """

    tag: str
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        tag = self.tag

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "tag": tag,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        tag = d.pop("tag")

        post_posts_post_id_tags_json_body = cls(
            tag=tag,
        )

        post_posts_post_id_tags_json_body.additional_properties = d
        return post_posts_post_id_tags_json_body

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
