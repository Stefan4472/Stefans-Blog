from typing import Any, Dict, List, Type, TypeVar

import attr

T = TypeVar("T", bound="PostCommandsPublishJsonBody")


@attr.s(auto_attribs=True)
class PostCommandsPublishJsonBody:
    """
    Attributes:
        post_id (int): ID of the post to publish
        send_email (bool): Whether to trigger sending an update email to all subscribers.
    """

    post_id: int
    send_email: bool
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        post_id = self.post_id
        send_email = self.send_email

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "post_id": post_id,
                "send_email": send_email,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        post_id = d.pop("post_id")

        send_email = d.pop("send_email")

        post_commands_publish_json_body = cls(
            post_id=post_id,
            send_email=send_email,
        )

        post_commands_publish_json_body.additional_properties = d
        return post_commands_publish_json_body

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
