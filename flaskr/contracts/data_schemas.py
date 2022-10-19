import dataclasses as dc
from datetime import datetime
from typing import Dict, List
# TODO: this feels inefficient to me. However, it is good to have defined contract structs


@dc.dataclass
class UserContract:
    id: int
    name: str

    def make_json(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
        }


@dc.dataclass
class TagContract:
    slug: str
    name: str
    description: str
    color: str

    def make_json(self) -> Dict:
        return {
            'slug': self.slug,
            'name': self.name,
            'description': self.description,
            'color': self.color,
        }


@dc.dataclass
class FileContract:
    id: str
    upload_name: str
    upload_date: datetime
    uploaded_by: UserContract
    filetype: str
    filename: str
    url: str
    size: int
    hash: str

    def make_json(self) -> Dict:
        return {
            'id': self.id,
            'upload_name': self.upload_name,
            'upload_date': str(self.upload_date),
            'uploaded_by': self.uploaded_by.make_json(),
            'filetype': self.filetype.value,
            'filename': self.filename,
            'url': self.url,
            'size': self.size,
            'hash': self.hash,
        }


@dc.dataclass
class PostContract:
    id: int
    author: UserContract
    last_modified: datetime
    is_featured: bool
    is_published: bool
    slug: str = None
    title: str = None
    byline: str = None
    publish_date: datetime = None
    featured_image: FileContract = None
    banner_image: FileContract = None
    thumbnail_image: FileContract = None
    tags: List[TagContract] = None

    def make_json(self) -> Dict:
        return {
            'id': self.id,
            'author': self.author.make_json(),
            'last_modified': str(self.last_modified),
            'is_featured': self.is_featured,
            'is_published': self.is_published,
            'slug': self.slug,
            'title': self.title,
            'byline': self.byline,
            'publish_date': str(self.publish_date),
            'featured_image': self.featured_image.make_json(),
            'banner_image': self.banner_image.make_json(),
            'thumbnail_image': self.thumbnail_image.make_json(),
            'tags': [t.make_json() for t in self.tags],
        }
