import dataclasses as dc
from datetime import datetime
from typing import Dict, List, Optional
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
    slug: str
    title: str
    byline: str
    publish_date: Optional[datetime]
    featured_image: Optional[FileContract]
    banner_image: Optional[FileContract]
    thumbnail_image: Optional[FileContract]
    tags: List[TagContract]
    is_featured: bool
    is_published: bool

    def make_json(self) -> Dict:
        res = {
            'id': self.id,
            'author': self.author.make_json(),
            'last_modified': str(self.last_modified),
            'slug': self.slug,
            'title': self.title,
            'byline': self.byline,
            'tags': [t.make_json() for t in self.tags],
            'is_featured': self.is_featured,
            'is_published': self.is_published,
        }
        if self.publish_date:
            res['publish_date'] = str(self.publish_date)
        if self.featured_image:
            res['featured_image'] = self.featured_image.make_json()
        if self.banner_image:
            res['banner_image'] = self.banner_image.make_json()
        if self.thumbnail_image:
            res['thumbnail_image'] = self.thumbnail_image.make_json()
        return res
