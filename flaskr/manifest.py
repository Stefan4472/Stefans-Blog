import json
import typing
import hashlib
import pathlib
import io
import dataclasses as dc
from PIL import Image
from . import manage_util as util
"""NOTE: this code is in its first iteration, and is likely difficult to understand."""


class ManifestFile(typing.NamedTuple):
    hash: str
    post_slug: str
    filename: str


@dc.dataclass
class FileToAdd:
    contents: io.BytesIO
    hash: str
    post_slug: str
    filename: str

    def to_manifest_file(self) -> ManifestFile:
        return ManifestFile(self.hash, self.post_slug, self.filename)


@dc.dataclass
class PostDiff:
    slug: str
    write_files: typing.List[ManifestFile] = dc.field(default_factory=list)
    del_files: typing.List[ManifestFile] = dc.field(default_factory=list)


# @dc.dataclass
# class SyncDiff:
#     add_files: typing.List[str] = dc.field(default_factory=list)
#     rmv_files: typing.List[str] = dc.field(default_factory=list)
#     overwrite_files: typing.List[str] = dc.field(default_factory=list)


class Manifest:
    """The Manifest records all files required by the local site 
    instance's posts.

    The Manifest writes to a json file, which has one top level 'posts'
    dictionary. Within the 'posts' dict, it is organized as follows:
    ```
    [post slug]: {
        [filename]: {
            "hash": [MD-5 hashed contents of file]
        }
        ...
    }
    ```
    Each post slug is listed, and contains a dictionary of needed files. Each
    file has a calculated hash.

    The Manifest allows us to determine which files need to be written or
    deleted whenever we add a post. When pushing to production, it allows
    us to compare the local manifest to the remote manifest, and then only
    copy the files that have changed.

    One drawback of the current implementation of the manifest is that we
    assume the file system has not been modified from that set by the site.
    If the user does something that makes the filesystem no longer reflect 
    the manifest, we have no way of knowing.

    Because of this, it is important that the `static` post folders are never
    changed by the user outside of this program!
    """
    def __init__(
            self,
            filepath: str,
    ):
        self.filepath = filepath
        try:
            with open(self.filepath, encoding='utf8') as manifest_file:
                self.json_data = json.load(manifest_file)  # TODO: THIS WILL FALL OUT OF DATE WITH POST_DATA
                self.post_data = self.json_data['posts']
        except FileNotFoundError:
            # Create manifest and write blank json file
            self.json_data = {'posts': {}}
            self.post_data = self.json_data['posts']
            self.commit()
        except json.JSONDecodeError as e:
            raise ValueError(
                'Could not read manifest file: invalid JSON ({})'.format(str(e))
            )

    def clear(self):
        """Clears the manifest file. DANGEROUS! Only use when resetting 
        the whole site."""
        self.json_data = {'posts': {}}
        self.commit()

    def calc_addpost_diff(
            self,
            post_slug: str,
            post_files: typing.Dict[str, FileToAdd],
    ) -> PostDiff:
        """Note: assumes all post_files have the same post_slug"""
        # Make sure that all `post_files` share the specified slug
        for f in post_files.values():
            if f.post_slug != post_slug:
                raise ValueError('Found inconsistent post slug')

        diff = PostDiff(post_slug)

        # A post with this slug already exists
        if post_slug in self.post_data:
            curr_post_data = self.post_data[post_slug]
            
            # Get set of current filenames registered with that post 
            curr_post_filenames = set([filename for filename in curr_post_data])
            
            # Go through the `post_files` one by one, determining what needs 
            # to be added, removed, or overwritten
            for add_filename, add_file in post_files.items():
                # This file is registered: compare hashes
                if add_filename in curr_post_data:
                    # Hash is the same: no need to do anything
                    if add_file.hash == curr_post_data[add_filename]['hash']:
                        pass
                    # Hash is different: mark this file for overwrite
                    else:
                        diff.write_files.append(add_file.to_manifest_file())
                    # Remove this file from `curr_post_filenames`
                    curr_post_filenames.remove(add_filename)
                # This file is not registered: mark for addition
                else:
                    diff.write_files.append(add_file.to_manifest_file())
            
            # Any files remaining in the `curr_post_filenames` set are no
            # longer needed: mark them for deletion
            for filename in curr_post_filenames:
                diff.del_files.append(ManifestFile(
                    curr_post_data[filename]['hash'],
                    post_slug,
                    curr_post_data[filename],
                ))
            pass
        # No post with this slug exists: add everything
        else:
            for post_file in post_files.values():
                diff.write_files.append(post_file.to_manifest_file())
        return diff

    def apply_addpost_diff(
            self,
            post_diff: PostDiff,
            files_to_add: typing.Dict[str, FileToAdd],
            static_path: pathlib.Path,
    ):  
        # Build post's static path and create dir if it doesn't already exist
        post_static_path = static_path / post_diff.slug
        post_static_path.mkdir(exist_ok=True)

        # Add nested dictionary for the specified slug if it doesn't exist yet
        if post_diff.slug not in self.post_data:
            self.post_data[post_diff.slug] = {}

        # Write files
        for manifest_file in post_diff.write_files:
            # Lookup the `FileToAdd` instance, which has the file contents 
            # in-memory
            file_to_add = files_to_add[manifest_file.filename]
            # Generate full path 
            add_path = post_static_path / file_to_add.filename
            # Write file
            with open(add_path, 'wb') as out:
                out.write(file_to_add.contents.getbuffer())
            # Update manifest
            self.post_data[post_diff.slug][manifest_file.filename] = {
                'hash': file_to_add.hash,
            }
            
        # Delete files
        for manifest_file in post_diff.del_files:
            # Generate full path 
            rmv_path = post_static_path / manifest_file.filename
            # Delete file
            rmv_path.unlink()
            # Update manifest
            del self.json_data[post_diff.slug][manifest_file.filename]

        # Write out manifest
        self.commit()  # TODO: TELL USER TO COMMIT?

    def calc_manifest_diff(
            self,
            other_manifest: 'Manifest',
    ):
        """Calculate diff between this manifest and a different manifest."""
        return
        
    def commit(self):
        with open(self.filepath, 'w', encoding='utf8') as manifest_file:
            json.dump(self.json_data, manifest_file, indent=4)


def prepare_image(
        post_image: util.PostImage,
        post_slug: str,
        filename: str,
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
        post_slug,
        filename,
    ) 


def prepare_text(
        string: str,
        post_slug: str,
        filename: str,
) -> FileToAdd:
    str_byte_array = io.BytesIO()
    str_byte_array.write(string.encode())
    str_hash = hashlib.md5(str_byte_array.getvalue())
    
    return FileToAdd(
        str_byte_array,
        str_hash.hexdigest(),
        post_slug,
        filename,
    )


def prepare_files_for_add(
        post_data: util.PostData,
        post_static_rel_path: str,
) -> typing.Dict[str, FileToAdd]:
    """Transforms a `PostData` instance into a dictionary of `FileToAdd`
    instances (mapped by filename)."""
    files_to_add: typing.Dict[FileToAdd] = {}

    files_to_add['post.html'] = \
        prepare_text(post_data.html, post_data.slug, 'post.html')
    files_to_add['featured.jpg'] = \
        prepare_image(post_data.featured_img, post_data.slug, 'featured.jpg')
    files_to_add['thumbnail.jpg'] = \
        prepare_image(post_data.thumbnail_img, post_data.slug, 'thumbnail.jpg')
    files_to_add['banner.jpg'] = \
        prepare_image(post_data.banner_img, post_data.slug, 'banner.jpg')

    for post_img in post_data.images:
        files_to_add[post_img.path.name] = \
            prepare_image(post_img, post_data.slug, post_img.path.name)
    
    return files_to_add
