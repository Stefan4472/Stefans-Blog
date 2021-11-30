import datetime
import pathlib
import json
import typing
import dataclasses as dc
import tkinter as tk
from tkinter.filedialog import askopenfilename
from sitemanager import util
from imagecropper.imagecropper import ImageCropper


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
    # Note: these two value are not read from JSON
    publish: typing.Optional[bool] = None
    feature: typing.Optional[bool] = None
    title_color: typing.Optional[str] = None

    def to_json(self) -> dict:
        _json = {
            util.KEY_SLUG: self.slug,
            util.KEY_TITLE: self.title,
            util.KEY_BYLINE: self.byline,
            util.KEY_DATE: self.date.strftime(util.DATE_FORMAT),
            util.KEY_TAGS: self.tags,
            util.KEY_IMAGE: self.featured_img.name,
            util.KEY_BANNER: self.banner_img.name,
            util.KEY_THUMBNAIL: self.thumbnail_img.name,
        }
        if self.publish is not None:
            _json[util.KEY_PUBLISH] = self.publish
        if self.feature is not None:
            _json[util.KEY_FEATURE] = self.feature
        if self.title_color is not None:
            _json[util.KEY_TITLE_COLOR] = self.title_color
        return _json


def read_config_file(
        filepath: pathlib.Path,
        use_imagecropper: bool = True,
) -> 'PostConfig':
    """
    Read a `PostConfig` file. Set `use_imagecropper` to True to open
    ImageCropper if a post image (featured, banner, thumbnail) is missing.
    """
    # Load JSON
    try:
        with open(filepath, 'r', encoding='utf-8', errors='strict') as f:
            cfg_json = json.load(f)
    except IOError:
        msg = 'Could not open the config file at ("{}")'.format(filepath.resolve())
        raise ValueError(msg)
    except json.JSONDecodeError as e:
        msg = 'Invalid JSON in the provided config file: {}'.format(str(e))
        raise ValueError(msg)

    if util.KEY_TITLE not in cfg_json:
        raise ValueError('Missing title ("{}")'.format(util.KEY_TITLE))
    if util.KEY_BYLINE not in cfg_json:
        raise ValueError('Missing byline ("{}")'.format(util.KEY_BYLINE))
    if util.KEY_DATE not in cfg_json:
        raise ValueError('Missing date ("{}")'.format(util.KEY_DATE))

    # Run Imagecropper if images are missing
    if util.KEY_IMAGE not in cfg_json or \
            util.KEY_BANNER not in cfg_json or \
            util.KEY_THUMBNAIL not in cfg_json and use_imagecropper:
        img_path, thumb_path, banner_path = run_image_cropper(filepath.parent)
        cfg_json[util.KEY_IMAGE] = img_path.name
        cfg_json[util.KEY_THUMBNAIL] = thumb_path.name
        cfg_json[util.KEY_BANNER] = banner_path.name
    elif util.KEY_IMAGE not in cfg_json:
        raise ValueError('Missing featured ("{}")'.format(util.KEY_IMAGE))
    elif util.KEY_BANNER not in cfg_json:
        raise ValueError('Missing banner ("{}")'.format(util.KEY_BANNER))
    elif util.KEY_THUMBNAIL not in cfg_json:
        raise ValueError('Missing thumbnail ("{}")'.format(util.KEY_THUMBNAIL))

    # Note: generates slug from title if none is specified by the user
    return PostConfig(
        cfg_json[util.KEY_SLUG] if util.KEY_SLUG in cfg_json else util.generate_slug(cfg_json[util.KEY_TITLE]),
        cfg_json[util.KEY_TITLE],
        cfg_json[util.KEY_BYLINE],
        datetime.datetime.strptime(cfg_json[util.KEY_DATE], util.DATE_FORMAT).date(),
        cfg_json[util.KEY_TAGS] if util.KEY_TAGS in cfg_json else [],
        pathlib.Path((filepath.parent / cfg_json[util.KEY_IMAGE]).resolve()),
        pathlib.Path((filepath.parent / cfg_json[util.KEY_THUMBNAIL]).resolve()),
        pathlib.Path((filepath.parent / cfg_json[util.KEY_BANNER]).resolve()),
        publish=cfg_json[util.KEY_PUBLISH] if util.KEY_PUBLISH in cfg_json else None,
        feature=cfg_json[util.KEY_FEATURE] if util.KEY_FEATURE in cfg_json else None,
        title_color=cfg_json[util.KEY_TITLE_COLOR] if util.KEY_TITLE_COLOR in cfg_json else None,
    )


def write_config_file(
        config: PostConfig,
        filepath: pathlib.Path,
):
    """Write `PostConfig` instance out to specified filepath."""
    cfg_json = config.to_json()
    if util.KEY_PUBLISH in cfg_json:
        cfg_json.pop(util.KEY_PUBLISH)
    if util.KEY_FEATURE in cfg_json:
        cfg_json.pop(util.KEY_FEATURE)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(cfg_json, f, indent=4)


def run_image_cropper(
        post_dir: pathlib.Path,
) -> typing.Tuple[pathlib.Path, pathlib.Path, pathlib.Path]:
    root = tk.Tk()
    # Ask user to select an image for use
    img_path = askopenfilename(
        initialdir=post_dir,
        title='Select featured image',
        filetypes=(
            ('jpg files', '*.jpg'),
            ('jpeg files', '*.jpeg'),
            ('png files', '*.png'),
            ('gif files', '*.gif'),
        ),
    )
    # Exit if user did not select an image
    if not img_path:
        raise ValueError('No image selected')

    img_path = pathlib.Path(img_path)

    # Create featured image
    app = ImageCropper(img_path, util.FEATURED_IMG_SIZE[0], util.FEATURED_IMG_SIZE[1])
    app.mainloop()
    if app.finished_successfully:
        featured_img = app.cropped_image
    else:
        raise ValueError('Operation cancelled')

    # Create thumbnail
    app = ImageCropper(str(img_path), util.THUMBNAIL_SIZE[0], util.THUMBNAIL_SIZE[1])
    app.mainloop()
    if app.finished_successfully:
        thumbnail_img = app.cropped_image
    else:
        raise ValueError('Operation cancelled')

    # Create banner
    app = ImageCropper(img_path, util.BANNER_SIZE[0], util.BANNER_SIZE[1])
    app.mainloop()
    if app.finished_successfully:
        banner_img = app.cropped_image
    else:
        raise ValueError('Operation cancelled')

    # Create the paths for the newly-cropped images
    featured_path = post_dir / 'featured.jpg'
    thumbnail_path = post_dir / 'thumb.jpg'
    banner_path = post_dir / 'banner.jpg'

    # Save the images
    featured_img.save(featured_path)
    thumbnail_img.save(thumbnail_path)
    banner_img.save(banner_path)

    return featured_path, thumbnail_path, banner_path
