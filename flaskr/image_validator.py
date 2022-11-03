from PIL import Image
from typing import Optional, Tuple
from flaskr.models.file import File, FileType
from flaskr import file_manager
from flaskr.api.constants import FEATURED_IMG_SIZE, BANNER_SIZE, THUMBNAIL_SIZE


def is_featured_image_valid(file_id: Optional[str]) -> bool:
    return _is_image_valid(file_id, FEATURED_IMG_SIZE)


def is_banner_image_valid(file_id: Optional[str]) -> bool:
    return _is_image_valid(file_id, BANNER_SIZE)


def is_thumbnail_image_valid(file_id: Optional[str]) -> bool:
    return _is_image_valid(file_id, THUMBNAIL_SIZE)


def _is_image_valid(
        file_id: str,
        required_dimensions: Tuple[int, int],
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
    return (as_image.width, as_image.height) == required_dimensions
