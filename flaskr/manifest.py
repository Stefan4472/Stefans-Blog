import json
import typing
import hashlib
import pathlib
import io
import dataclasses as dc
from PIL import Image
import flaskr.manage_util as util


@dc.dataclass
class FileToAdd:
    contents: io.BytesIO
    hash: str
    rel_static_path: str


@dc.dataclass
class FileHash:
    # MD5 hash digest of file contents
    hash: str
    # Whether the file is currently in-memory only
    in_memory_only: bool
    # File size, bytes
    filesize: int = 0  # TODO
    # Full path to the file. Will be `None` if `in_memory` is True
    filepath: typing.Optional[pathlib.Path] = None
    # Relative path from 'static' to where the file will be/is
    static_rel_path: str = ''


@dc.dataclass
class PostHashes:
    html_hash: FileHash
    featured_img_hash: FileHash
    thumbnail_img_hash: FileHash
    banner_img_hash: FileHash
    image_hashes: typing.List[FileHash] = dc.field(default_factory=list)


@dc.dataclass
class PostDiff:
    add_files: typing.List[FileHash] = dc.field(default_factory=list)
    rmv_files: typing.List[FileHash] = dc.field(default_factory=list)
    overwrite_files: typing.List[FileHash] = dc.field(default_factory=list)


# @dc.dataclass
# class SyncDiff:
#     add_files: typing.List[str] = dc.field(default_factory=list)
#     rmv_files: typing.List[str] = dc.field(default_factory=list)
#     overwrite_files: typing.List[str] = dc.field(default_factory=list)


class Manifest:
    def __init__(
            self,
            filepath: str,
    ):
        self.filepath = filepath
        # print('manifest constructed with path {}'.format(self.filepath))
        # TODO: CATCH EXCEPTIONS
        try:
            with open(filepath, encoding='utf8') as manifest_file:
                self.json_data = json.load(manifest_file)
        except FileNotFoundError:
            # print('Creating manifest')
            # Create manifest and write blank json file
            with open(filepath, 'a', encoding='utf8') as manifest_file:
                manifest_file.write(r'{"posts":{}}')

    # def calc_addpost_diff(
    #         self,
    #         post_slug: str,
    #         post_files: typing.List[FileToAdd],
    # ) -> PostDiff:
    #     diff = PostDiff()
    #     # A post with this slug already exists
    #     if post_slug in self.json_data['posts']:
    #         pass
    #     # No post with this slug exists: add everything
    #     else:
    #         diff.add_files.append(post_hashes.html_hash)
    #         diff.add_files.append(post_hashes.featured_img_hash)
    #         diff.add_files.append(post_hashes.thumbnail_img_hash)
    #         diff.add_files.append(post_hashes.banner_img_hash)
    #         for img_hash in post_hashes.image_hashes:
    #             diff.add_files.append(img_hash)
    #     return diff

    # def apply_diffs()


def prepare_image(
        post_image: util.PostImage,
        rel_static_path: str,
) -> FileToAdd:
    # https://stackoverflow.com/a/33117447
    img_byte_array = io.BytesIO()
    # Save image to byte array
    post_image.image.save(img_byte_array, format=post_image.image.format)
    # Calculate MD5 hash of the image
    img_hash = hashlib.md5(img_byte_array.getvalue())

    return FileToAdd(
        img_byte_array,
        img_hash.hexdigest(),
        rel_static_path,
    ) 


def prepare_text(
        string: str,
        rel_static_path: str,
) -> FileToAdd:
    str_byte_array = io.BytesIO()
    str_byte_array.write(string.encode())
    str_hash = hashlib.md5(str_byte_array.getvalue())
    
    return FileToAdd(
        str_byte_array,
        str_hash.hexdigest(),
        rel_static_path,
    )


def prepare_files_for_add(
        post_data: util.PostData,
        post_static_rel_path: str,
) -> typing.List[FileToAdd]:
    files_to_add: typing.List[FileToAdd] = []
    static_path = post_static_rel_path
    
    files_to_add.append(
        prepare_text(post_data.html, static_path + '/post.html')
    )
    files_to_add.append(
        prepare_image(post_data.featured_img, static_path + '/featured.jpg')
    )
    files_to_add.append(
        prepare_image(post_data.thumbnail_img, static_path + '/thumbnail.jpg')
    )
    files_to_add.append(
        prepare_image(post_data.banner_img, static_path + '/banner.jpg')
    )

    for post_img in post_data.images:
        files_to_add.append(
            prepare_image(post_img, static_path + '/' + post_img.path.name)
        )
    return files_to_add

# def compute_hashes(
#         post_data: util.PostData,
#         post_static_rel_path: str,
# ) -> PostHashes:
#     post_hashes = PostHashes(
#         FileHash(hash_string(post_data.html), True, static_rel_path='/static/post.html'),
#         hash_image(post_data.featured_img),
#         hash_image(post_data.thumbnail_img),
#         hash_image(post_data.banner_img),
#     )

#     # Hash all images
#     for post_image in post_data.images:
#         post_hashes.image_hashes.append(hash_image(post_image))

#     return post_hashes