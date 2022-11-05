import json
import typing
import dataclasses as dc
from typing import Optional, List
from pathlib import Path
from datetime import datetime, date
from sos_client import constants


@dc.dataclass
class PostMeta:
    """Store post configuration ("post-meta") data."""
    slug: Optional[str] = None
    title: Optional[str] = None
    byline: Optional[str] = None
    date: Optional[date] = None
    tags: Optional[List[str]] = None
    image: Optional[Path] = None
    banner: Optional[Path] = None
    thumbnail: Optional[Path] = None

    # def to_json(self) -> dict:
    #     return {
    #         'slug': self.slug,
    #         'title': self.title,
    #         'byline': self.byline,
    #         'date': self.date.strftime(constants.DATE_FORMAT),
    #         'tags': self.tags,
    #         'featured_image': self.featured_img.absolute(),
    #         'banner_image': self.banner_img.absolute(),
    #         'thumbnail_image': self.thumbnail_img.absolute(),
    #     }

    @staticmethod
    def parse_from_file(filepath: Path) -> 'PostMeta':
        """Parse a `post-meta.json` file and return an instance of `PostConfig`."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='strict') as f:
                cfg_json = json.load(f)
        except IOError:
            raise ValueError(f'Could not open the config file at ("{filepath.absolute()}")')
        except json.JSONDecodeError as e:
            raise ValueError(f'Invalid JSON in the provided config file: {e}')
        # TODO: validation using marshmallow
        return PostMeta(**cfg_json)

    def write_to_file(self, filepath: Path):
        """Write `PostConfig` instance out to specified filepath."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'slug': self.slug,
                'title': self.title,
                'byline': self.byline,
                'date': self.date, #self.date.strftime(constants.DATE_FORMAT),
                'tags': self.tags,
                'image': str(self.image), #str(self.image.absolute()),
                'banner': str(self.banner), #str(self.banner.absolute()),
                'thumbnail': str(self.thumbnail), #str(self.thumbnail.absolute()),
            }, f, indent=4)
