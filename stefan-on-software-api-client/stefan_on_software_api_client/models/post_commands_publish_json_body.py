from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostCommandsPublishJsonBody")


@attr.s(auto_attribs=True)
class PostCommandsPublishJsonBody:
    """
    Attributes:
        post_id (int): ID of the post to publish
        send_email (bool): Whether to trigger sending an update email to all subscribers.
        publish_date (Union[Unset, str]): Override the publish_date for this post. Intended for use in migrations.
            Example: 2022-09-15 10:40:52+00:00.
    """

    post_id: int
    send_email: bool
    publish_date: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        post_id = self.post_id
        send_email = self.send_email
        publish_date = self.publish_date

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "post_id": post_id,
                "send_email": send_email,
            }
        )
        if publish_date is not UNSET:
            field_dict["publish_date"] = publish_date

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        post_id = d.pop("post_id")

        send_email = d.pop("send_email")

        publish_date = d.pop("publish_date", UNSET)

        post_commands_publish_json_body = cls(
            post_id=post_id,
            send_email=send_email,
            publish_date=publish_date,
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
