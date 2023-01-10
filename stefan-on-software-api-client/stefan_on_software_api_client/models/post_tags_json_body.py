from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostTagsJsonBody")


@attr.s(auto_attribs=True)
class PostTagsJsonBody:
    """
    Attributes:
        name (str): Name of the tag
        slug (str): Slug used to create a URL for the tag. Must be unique. Cannot be changed once created.
        description (str): Tag description
        color (Union[Unset, str]): Hex color for the tag. Will be randomly generated by the backend if none is provided
    """

    name: str
    slug: str
    description: str
    color: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        slug = self.slug
        description = self.description
        color = self.color

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "slug": slug,
                "description": description,
            }
        )
        if color is not UNSET:
            field_dict["color"] = color

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        slug = d.pop("slug")

        description = d.pop("description")

        color = d.pop("color", UNSET)

        post_tags_json_body = cls(
            name=name,
            slug=slug,
            description=description,
            color=color,
        )

        post_tags_json_body.additional_properties = d
        return post_tags_json_body

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
