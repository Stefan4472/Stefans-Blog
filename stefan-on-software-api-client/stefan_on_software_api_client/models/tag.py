from typing import Any, Dict, List, Type, TypeVar

import attr

T = TypeVar("T", bound="Tag")


@attr.s(auto_attribs=True)
class Tag:
    """A tag used to categorize posts

    Attributes:
        slug (str): Unique "slug" used to make the URL for this tag on the public website. Cannot be changed. Example:
            data-analysis.
        name (str): Human-readable name used when displaying the tag on the website Example: Data Analysis.
        description (str): A short description used to help readers understand the tag. Example: Posts that have to do
            with data analysis and visualization..
        color (str): Hex color used when displaying the tag Example: #FFFFFF.
    """

    slug: str
    name: str
    description: str
    color: str
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        slug = self.slug
        name = self.name
        description = self.description
        color = self.color

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "slug": slug,
                "name": name,
                "description": description,
                "color": color,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        slug = d.pop("slug")

        name = d.pop("name")

        description = d.pop("description")

        color = d.pop("color")

        tag = cls(
            slug=slug,
            name=name,
            description=description,
            color=color,
        )

        tag.additional_properties = d
        return tag

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
