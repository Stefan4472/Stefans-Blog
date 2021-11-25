import typing
import pathlib
import hashlib
import dataclasses as dc
from sitemanager import util


@dc.dataclass
class PostDiff:
    """Diff for a single post."""
    slug: str
    write_html: str = ''
    write_images: typing.List[pathlib.Path] = dc.field(default_factory=list)
    delete_images: typing.List[str] = dc.field(default_factory=list)


@dc.dataclass
class SiteDiff:
    """Diff for the whole site."""
    create_posts: typing.List[str] = dc.field(default_factory=list)
    delete_posts: typing.List[str] = dc.field(default_factory=list)
    post_diffs: typing.List[PostDiff] = dc.field(default_factory=list)


# TODO(?)
class Manifest:
    def __init__(self, _json: typing.Dict):
        self.posts: typing.Dict = _json['posts']

    def calc_post_diff(
            self,
            slug: str,
            html: str,
            images: [pathlib.Path],
    ) -> SiteDiff:
        """
        Calculates the diff created by adding a post with the given
        `slug` and `files`.
        """
        site_diff = SiteDiff()
        post_diff = PostDiff(slug)
        # Slug already exists in posts
        if slug in self.posts:
            remote_post = self.posts[slug]
            # Check for html change
            html_hash = hashlib.md5(html.encode('utf-8')).hexdigest()
            if html_hash != remote_post['hash']:
                post_diff.write_html = html
            # Get set of remote image filenames
            remote_images = set(remote_post['images'].keys())
            # Iterate through local images
            for local_image in images:
                if local_image.name in remote_images:
                    local_hash = util.calc_hash(local_image)
                    remote_hash = remote_post['images'][local_image.name]['hash']
                    print(local_image.name, local_hash, remote_hash)
                    # Check hash
                    if local_hash != remote_hash:
                        post_diff.write_images.append(local_image)
                    remote_images.remove(local_image.name)
                else:
                    post_diff.write_images.append(local_image)
            # Any remote images left should be deleted (don't appear locally)
            post_diff.delete_images = list(remote_images)
        # Slug doesn't exist: add everything
        else:
            site_diff.create_posts.append(slug)
            post_diff.write_html = html
            post_diff.write_images = images
        site_diff.post_diffs.append(post_diff)
        return site_diff
