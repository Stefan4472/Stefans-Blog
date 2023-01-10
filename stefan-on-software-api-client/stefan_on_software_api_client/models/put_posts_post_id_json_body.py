from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="PutPostsPostIdJsonBody")


@attr.s(auto_attribs=True)
class PutPostsPostIdJsonBody:
    """
    Attributes:
        slug (str):
        title (str):
        byline (str):
        featured_image (Union[Unset, str]):
        banner_image (Union[Unset, str]):
        thumbnail_image (Union[Unset, str]):
    """

    slug: str
    title: str
    byline: str
    featured_image: Union[Unset, str] = UNSET
    banner_image: Union[Unset, str] = UNSET
    thumbnail_image: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        slug = self.slug
        title = self.title
        byline = self.byline
        featured_image = self.featured_image
        banner_image = self.banner_image
        thumbnail_image = self.thumbnail_image

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "slug": slug,
                "title": title,
                "byline": byline,
            }
        )
        if featured_image is not UNSET:
            field_dict["featured_image"] = featured_image
        if banner_image is not UNSET:
            field_dict["banner_image"] = banner_image
        if thumbnail_image is not UNSET:
            field_dict["thumbnail_image"] = thumbnail_image

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        slug = d.pop("slug")

        title = d.pop("title")

        byline = d.pop("byline")

        featured_image = d.pop("featured_image", UNSET)

        banner_image = d.pop("banner_image", UNSET)

        thumbnail_image = d.pop("thumbnail_image", UNSET)

        put_posts_post_id_json_body = cls(
            slug=slug,
            title=title,
            byline=byline,
            featured_image=featured_image,
            banner_image=banner_image,
            thumbnail_image=thumbnail_image,
        )

        put_posts_post_id_json_body.additional_properties = d
        return put_posts_post_id_json_body

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
