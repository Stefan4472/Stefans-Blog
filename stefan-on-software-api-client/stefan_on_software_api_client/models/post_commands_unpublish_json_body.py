from typing import Any, Dict, List, Type, TypeVar

import attr

T = TypeVar("T", bound="PostCommandsUnpublishJsonBody")


@attr.s(auto_attribs=True)
class PostCommandsUnpublishJsonBody:
    """
    Attributes:
        post_id (int): ID of the post to unpublish
    """

    post_id: int
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        post_id = self.post_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "post_id": post_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        post_id = d.pop("post_id")

        post_commands_unpublish_json_body = cls(
            post_id=post_id,
        )

        post_commands_unpublish_json_body.additional_properties = d
        return post_commands_unpublish_json_body

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
