from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostPostsJsonBody")


@attr.s(auto_attribs=True)
class PostPostsJsonBody:
    """
    Attributes:
        slug (Union[Unset, str]):
        title (Union[Unset, str]):
        byline (Union[Unset, str]):
        featured_image (Union[Unset, str]):
        banner_image (Union[Unset, str]):
        thumbnail_image (Union[Unset, str]):
    """

    slug: Union[Unset, str] = UNSET
    title: Union[Unset, str] = UNSET
    byline: Union[Unset, str] = UNSET
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
        field_dict.update({})
        if slug is not UNSET:
            field_dict["slug"] = slug
        if title is not UNSET:
            field_dict["title"] = title
        if byline is not UNSET:
            field_dict["byline"] = byline
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
        slug = d.pop("slug", UNSET)

        title = d.pop("title", UNSET)

        byline = d.pop("byline", UNSET)

        featured_image = d.pop("featured_image", UNSET)

        banner_image = d.pop("banner_image", UNSET)

        thumbnail_image = d.pop("thumbnail_image", UNSET)

        post_posts_json_body = cls(
            slug=slug,
            title=title,
            byline=byline,
            featured_image=featured_image,
            banner_image=banner_image,
            thumbnail_image=thumbnail_image,
        )

        post_posts_json_body.additional_properties = d
        return post_posts_json_body

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
