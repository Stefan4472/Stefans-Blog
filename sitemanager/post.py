import datetime
import pathlib
import json
import typing
import dataclasses as dc
import util


@dc.dataclass
class PostConfig:
    slug: str
    title: str
    byline: str
    date: datetime.date
    tags: typing.List[str]
    featured_img: pathlib.Path
    thumbnail_img: pathlib.Path
    banner_img: pathlib.Path

    # TODO: PROBABLY SPLIT THIS OUT INTO ITS OWN FILE
    @staticmethod
    def from_file(filepath: pathlib.Path) -> 'PostConfig':
        try:
            with open(filepath, 'r', encoding='utf-8', errors='strict') as f:
                cfg_json = json.load(f)
        except IOError:
            msg = 'Could not open the config file at ("{}")'.format(filepath.resolve())
            raise ValueError(msg)
        except json.JSONDecodeError as e:
            msg = 'Invalid JSON in the provided config file: {}'.format(str(e))
            raise ValueError(msg)

        # TODO: PROBABLY GO THE ORIGINAL ROUTE WITH A HELPER FUNCTION THAT CAN
        #  FILL IN THINGS, E.G. USE IMAGECROPPER TO FILL IN IMAGES
        if util.KEY_TITLE not in cfg_json:
            raise ValueError('Missing title ("{}")'.format(util.KEY_TITLE))
        if util.KEY_BYLINE not in cfg_json:
            raise ValueError('Missing byline ("{}")'.format(util.KEY_BYLINE))
        if util.KEY_DATE not in cfg_json:
            raise ValueError('Missing date ("{}")'.format(util.KEY_DATE))
        if util.KEY_FEATURED not in cfg_json:
            raise ValueError('Missing featured ("{}")'.format(util.KEY_FEATURED))
        if util.KEY_BANNER not in cfg_json:
            raise ValueError('Missing banner ("{}")'.format(util.KEY_BANNER))
        if util.KEY_THUMBNAIL not in cfg_json:
            raise ValueError('Missing thumbnail ("{}")'.format(util.KEY_THUMBNAIL))

        # Generate slug from title if none is specified by the user
        # Parse the date in the format "MM/DD/YY"
        return PostConfig(
            cfg_json[util.KEY_SLUG] if util.KEY_SLUG in cfg_json else util.generate_slug(cfg_json[util.KEY_TITLE]),
            cfg_json[util.KEY_TITLE],
            cfg_json[util.KEY_BYLINE],
            datetime.datetime.strptime(cfg_json[util.KEY_DATE], "%m/%d/%y").date(),
            cfg_json[util.KEY_TAGS] if util.KEY_TAGS in cfg_json else [],
            pathlib.Path(cfg_json[util.KEY_FEATURED]),
            pathlib.Path(cfg_json[util.KEY_THUMBNAIL]),
            pathlib.Path(cfg_json[util.KEY_BANNER]),
        )


# @dc.dataclass
# class PostData:
#     """Container for all of the data needed to create a post."""
#     title: str
#     byline: str
#     slug: str
#     post_date: datetime.date
#     featured_img: pathlib.Path
#     thumbnail_img: pathlib.Path
#     banner_img: pathlib.Path
#     # List of tags
#     tag_names: typing.List[str] = dc.field(default_factory=list)
#     # Generated post HTML
#     html: str = ''
#     # All images that need to be uploaded with the post
#     image_paths: typing.List[pathlib.Path] = dc.field(default_factory=list)