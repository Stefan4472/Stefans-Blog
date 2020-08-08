import json
import typing
import hashlib
import io
import dataclasses as dc
from PIL import Image
import flaskr.manage_util as util


@dc.dataclass
class FileHash():
    hash: str
    filesize: int = 0  # TODO
    filepath: str = ''

@dc.dataclass
class PostHashes():
    html_hash: FileHash
    featured_img_hash: FileHash
    thumbnail_img_hash: FileHash
    banner_img_hash: FileHash
    image_hashes: typing.List[FileHash] = dc.field(default_factory=list)


class Manifest:
    def __init__(
            self,
            filepath: str,
    ):
        self.filepath = filepath
        self.json_data = {}
        # print('manifest constructed with path {}'.format(self.filepath))
        # TODO: CATCH EXCEPTIONS
        try:
            with open(filepath, encoding='utf8') as manifest_file:
                json_data = json.load(manifest_file)
        except FileNotFoundError:
            # print('Creating manifest')
            # Create manifest and write blank json file
            with open(filepath, 'a', encoding='utf8') as manifest_file:
                manifest_file.write(r'{"posts":{}}')

    # def get_post_diff(
    #         self,


def hash_image(image: Image.Image) -> FileHash:
    # https://stackoverflow.com/a/33117447
    img_byte_array = io.BytesIO()
    # Save image to byte array
    image.save(img_byte_array, format=image.format)
    # Calculate MD5 hash of the image
    img_hash = hashlib.md5(img_byte_array.getvalue())
    return FileHash(img_hash.hexdigest())


def hash_string(string: str) -> str:
    return hashlib.md5(string.encode()).hexdigest()


def compute_hashes(
        post_data: util.PostData,
) -> PostHashes:
    post_hashes = PostHashes(
        hash_string(post_data.html),
        hash_image(post_data.featured_img.image),
        hash_image(post_data.thumbnail_img.image),
        hash_image(post_data.banner_img.image),
    )

    # Hash all images
    for post_image in post_data.images:
        post_hashes.image_hashes.append(hash_image(post_image.image))

    return post_hashes