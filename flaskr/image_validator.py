from PIL import Image
from typing import Optional
from flaskr.models.file import File, FileType
import flaskr.contracts.constants as constants


def is_featured_image_valid(file_id: Optional[str]) -> bool:
    return _is_image_valid(file_id, constants.FEATURED_IMAGE_WIDTH, constants.FEATURED_IMAGE_HEIGHT)


def is_banner_image_valid(file_id: Optional[str]) -> bool:
    return _is_image_valid(file_id, constants.BANNER_WIDTH, constants.BANNER_HEIGHT)


def is_thumbnail_image_valid(file_id: Optional[str]) -> bool:
    return _is_image_valid(file_id, constants.THUMBNAIL_WIDTH, constants.THUMBNAIL_HEIGHT)


def _is_image_valid(
        file_id: str,
        required_width: int,
        required_height: int,
        allow_none: bool = True,
) -> bool:
    if file_id is None:
        return allow_none
    file = File.query.filter_by(id=file_id).first()
    # File does not exist
    if file is None:
        return False
    # File is not an image
    if file.filetype != FileType.Image:
        return False
    # File is a gif
    if file.filename.endswith('.gif'):
        return False
    as_image = Image.open(file.get_path())
    return as_image.width == required_width and as_image.height == required_height
