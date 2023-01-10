from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.file import File
    from ..models.tag import Tag
    from ..models.user import User


T = TypeVar("T", bound="Post")


@attr.s(auto_attribs=True)
class Post:
    """A post on the website.

    Attributes:
        id (int): Unique integer ID assigned to this post. Example: 15.
        author (User): A registered user
        last_modified (str): Timestamp at which this post was last modified. Example: 2022-09-15 10:40:52+00:00.
        slug (Union[Unset, str]): Unique "slug" used to make the URL for this post on the public website. Because the
            post URL (when published) is based on the slug, changing the slug will change the post's URL. Example: gamedev-
            spritesheets.
        title (Union[Unset, str]): Title of the post. Example: How to implement Spritesheets.
        byline (Union[Unset, str]): A short summary of the post that will be displayed when the post appears in a
            listing. It may also be used in the HTML description tag of the post on the public website, and when sending an
            email notification. Example: In this post we'll use Java to implement a Spritesheet class, with which we can
            play back hand-drawn animation sequences..
        publish_date (Union[Unset, str]): Timestamp at which this post was published. Will be null if the post is not
            currently published. Example: 2022-09-10 17:22:12+00:00.
        featured_image (Union[Unset, File]): A file stored on the webserver
        banner_image (Union[Unset, File]): A file stored on the webserver
        thumbnail_image (Union[Unset, File]): A file stored on the webserver
        tags (Union[Unset, List['Tag']]): Tags associated with this post.
        is_featured (Union[Unset, bool]): Whether this post is currently featured.
        is_published (Union[Unset, bool]): Whether this post is currently published. Example: True.
    """

    id: int
    author: "User"
    last_modified: str
    slug: Union[Unset, str] = UNSET
    title: Union[Unset, str] = UNSET
    byline: Union[Unset, str] = UNSET
    publish_date: Union[Unset, str] = UNSET
    featured_image: Union[Unset, "File"] = UNSET
    banner_image: Union[Unset, "File"] = UNSET
    thumbnail_image: Union[Unset, "File"] = UNSET
    tags: Union[Unset, List["Tag"]] = UNSET
    is_featured: Union[Unset, bool] = UNSET
    is_published: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        author = self.author.to_dict()

        last_modified = self.last_modified
        slug = self.slug
        title = self.title
        byline = self.byline
        publish_date = self.publish_date
        featured_image: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.featured_image, Unset):
            featured_image = self.featured_image.to_dict()

        banner_image: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.banner_image, Unset):
            banner_image = self.banner_image.to_dict()

        thumbnail_image: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.thumbnail_image, Unset):
            thumbnail_image = self.thumbnail_image.to_dict()

        tags: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.tags, Unset):
            tags = []
            for tags_item_data in self.tags:
                tags_item = tags_item_data.to_dict()

                tags.append(tags_item)

        is_featured = self.is_featured
        is_published = self.is_published

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "author": author,
                "last_modified": last_modified,
            }
        )
        if slug is not UNSET:
            field_dict["slug"] = slug
        if title is not UNSET:
            field_dict["title"] = title
        if byline is not UNSET:
            field_dict["byline"] = byline
        if publish_date is not UNSET:
            field_dict["publish_date"] = publish_date
        if featured_image is not UNSET:
            field_dict["featured_image"] = featured_image
        if banner_image is not UNSET:
            field_dict["banner_image"] = banner_image
        if thumbnail_image is not UNSET:
            field_dict["thumbnail_image"] = thumbnail_image
        if tags is not UNSET:
            field_dict["tags"] = tags
        if is_featured is not UNSET:
            field_dict["is_featured"] = is_featured
        if is_published is not UNSET:
            field_dict["is_published"] = is_published

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.file import File
        from ..models.tag import Tag
        from ..models.user import User

        d = src_dict.copy()
        id = d.pop("id")

        author = User.from_dict(d.pop("author"))

        last_modified = d.pop("last_modified")

        slug = d.pop("slug", UNSET)

        title = d.pop("title", UNSET)

        byline = d.pop("byline", UNSET)

        publish_date = d.pop("publish_date", UNSET)

        _featured_image = d.pop("featured_image", UNSET)
        featured_image: Union[Unset, File]
        if isinstance(_featured_image, Unset):
            featured_image = UNSET
        else:
            featured_image = File.from_dict(_featured_image)

        _banner_image = d.pop("banner_image", UNSET)
        banner_image: Union[Unset, File]
        if isinstance(_banner_image, Unset):
            banner_image = UNSET
        else:
            banner_image = File.from_dict(_banner_image)

        _thumbnail_image = d.pop("thumbnail_image", UNSET)
        thumbnail_image: Union[Unset, File]
        if isinstance(_thumbnail_image, Unset):
            thumbnail_image = UNSET
        else:
            thumbnail_image = File.from_dict(_thumbnail_image)

        tags = []
        _tags = d.pop("tags", UNSET)
        for tags_item_data in _tags or []:
            tags_item = Tag.from_dict(tags_item_data)

            tags.append(tags_item)

        is_featured = d.pop("is_featured", UNSET)

        is_published = d.pop("is_published", UNSET)

        post = cls(
            id=id,
            author=author,
            last_modified=last_modified,
            slug=slug,
            title=title,
            byline=byline,
            publish_date=publish_date,
            featured_image=featured_image,
            banner_image=banner_image,
            thumbnail_image=thumbnail_image,
            tags=tags,
            is_featured=is_featured,
            is_published=is_published,
        )

        post.additional_properties = d
        return post

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
