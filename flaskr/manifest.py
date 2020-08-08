import json
import typing
import hashlib
import pathlib
import io
import dataclasses as dc
from PIL import Image
import flaskr.manage_util as util


# TODO: ACTUALLY, WE DO NEED TO KNOW THE ASSOCIATED SLUG, SO THAT WE CAN
# REMOVE FILES THAT ARE NO LONGER NEEDED
@dc.dataclass
class FileToAdd:
    contents: io.BytesIO
    hash: str
    post_slug: str
    filename: str


class ManifestFile(typing.NamedTuple):
    hash: str
    post_slug: str
    filename: str

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
    def __init__(
            self,
            filepath: str,
    ):
        self.filepath = filepath
        # print('manifest constructed with path {}'.format(self.filepath))
        # TODO: CATCH EXCEPTIONS
        try:
            with open(self.filepath, encoding='utf8') as manifest_file:
                self.json_data = json.load(manifest_file)
        except FileNotFoundError:
            # print('Creating manifest')
            # Create manifest and write blank json file
            with open(filepath, 'a', encoding='utf8') as manifest_file:
                manifest_file.write(r'{"posts":{}}')

    def calc_addpost_diff(
            self,
            post_slug: str,
            post_files: typing.List[FileToAdd],
    ) -> PostDiff:
        """Note: assumes all post_files have the same post_slug"""
        diff = PostDiff(post_slug)
        for f in post_files:
            if f.post_slug != post_slug:
                raise ValueError('Found inconsistent post slug')

        # A post with this slug already exists
        if post_slug in self.json_data['posts']:
            curr_post_data = self.json_data['posts'][post_slug]
            # Get set of current filenames registered with that post 
            curr_post_filenames = \
                set([filename for filename in curr_post_data])
            # Go through the `post_files` one by one, determining what needs 
            # to be added, removed, or overwritten
            for post_file in post_files:
                # This file is registered: compare hashes
                if post_file.filename in curr_post_data:
                    # Hash is different: mark this file for overwrite
                    if post_file.hash != curr_post_data[post_file.filename]['hash']:
                        diff.write_files.append(ManifestFile(
                            post_file.hash,
                            post_file.slug,
                            post_file.filename,
                        ))
                    # Remove this file from `curr_post_filenames`
                    curr_post_filenames.remove(post_file.filename)
                # This file is not registered: mark for addition
                else:
                    diff.write_files.append(ManifestFile(
                        post_file.hash,
                        post_file.slug,
                        post_file.filename,
                    ))
            # Mark any files that are no longer used for deletion
            for filename in curr_post_filenames:
                diff.del_files.append(ManifestFile(
                    curr_post_data[filename]['hash'],
                    post_slug,
                    curr_post_data[filename],
                ))
            pass
        # No post with this slug exists: add everything
        else:
            for post_file in post_files:
                diff.write_files.append(ManifestFile(
                    post_file.hash,
                    post_file.post_slug,
                    post_file.filename,
                ))
        return diff

    def apply_addpost_diff(
            self,
            post_diff: PostDiff,
            files_to_add: typing.List[FileToAdd],
            static_path: pathlib.Path,
    ):  
        # TODO: MAKE 'FILES_TO_ADD' A DICT MAPPED BY FILENAME

        # Write files
        for manifest_file in post_diff.write_files:
            file_to_add: FileToAdd = None
            for f_to_add in files_to_add:
                if f_to_add.filename == manifest_file.filename:
                    file_to_add = f_to_add
            # Generate full path 
            add_path = static_path / file_to_add.post_slug / file_to_add.filename
            # Write out
            with open(add_path, 'wb') as out:
                out.write(file_to_add.contents.getbuffer())
            print('Wrote to {}'.format(add_path))

            # Build nested dictionary if not already exists
            if post_diff.slug not in self.json_data['posts']:
                self.json_data['posts'][post_diff.slug] = {}
            if manifest_file.filename not in self.json_data['posts'][post_diff.slug]:
                self.json_data['posts'][post_diff.slug][manifest_file.filename] = {}
            
            # Update manifest
            self.json_data['posts'][post_diff.slug][manifest_file.filename]['hash'] = file_to_add.hash
            
        # Delete files
        for manifest_file in post_diff.del_files:
            # Generate full path 
            rmv_path = static_path / manifest_file.post_slug / manifest_file.filename
            # Delete file
            rmv_path.unlink()
            print('Deleted {}'.format(rmv_path))
            # Update manifest
            del self.json_data[post_diff.slug][manifest_file.filename]
        # Write out manifest
        self.commit()

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
) -> typing.List[FileToAdd]:
    files_to_add: typing.List[FileToAdd] = []
    static_path = post_static_rel_path
    
    files_to_add.append(
        prepare_text(post_data.html, post_data.slug, 'post.html')
    )
    files_to_add.append(
        prepare_image(post_data.featured_img, post_data.slug, 'featured.jpg')
    )
    files_to_add.append(
        prepare_image(post_data.thumbnail_img, post_data.slug, 'thumbnail.jpg')
    )
    files_to_add.append(
        prepare_image(post_data.banner_img, post_data.slug, 'banner.jpg')
    )

    for post_img in post_data.images:
        files_to_add.append(
            prepare_image(post_img, post_data.slug, post_img.path.name)
        )
    return files_to_add
