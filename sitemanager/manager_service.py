import requests
import pathlib
import dataclasses as dc
from manifest import Manifest, SiteDiff
# TODO: EXCEPTIONS


@dc.dataclass
class ManagerService:
    base_url: str
    api_key: str

    def create_post(self, slug: str):
        print('Creating...')
        res = requests.post(
            '{}/api/v1/posts/{}'.format(self.base_url, slug),
            headers={'Authorization': self.api_key},
        )
        print(res)

    def delete_post(self, slug: str):
        print('Deleting...')
        res = requests.delete(
            '{}/api/v1/posts/{}'.format(self.base_url, slug),
            headers={'Authorization': self.api_key},
        )
        print(res)

    def upload_html(self, slug: str, html: str):
        print('Uploading HTML...')
        res = requests.post(
            '{}/api/v1/posts/{}/body'.format(self.base_url, slug),
            files={'file': ('post.html', html)},
            headers={'Authorization': self.api_key},
        )
        print(res)

    def upload_image(self, slug: str, path: pathlib.Path):
        print('Uploading image {}'.format(path))
        with open(path, 'rb') as f:
            res = requests.post(
                '{}/api/v1/posts/{}/images'.format(self.base_url, slug),
                files={'file': f},
                headers={'Authorization': self.api_key},
            )
            print(res)

    def delete_image(self, slug: str, filename: str):
        print('Deleting image')
        url = '{}/api/v1/posts/{}/images/{}'.format(
            self.base_url,
            slug,
            filename,
        )
        res = requests.delete(
            url,
            headers={'Authorization': self.api_key},
        )
        print(res)

    # TODO: META DATACLASS
    # TODO: RENAME TO `SET_CONFIG`. WHERE IS THIS USED?
    def set_meta(self, slug: str, meta: dict):
        print('Setting meta...')
        res = requests.post(
            '{}/api/v1/posts/{}/meta'.format(self.base_url, slug),
            json=meta,
            headers={'Authorization': self.api_key},
        )
        print(res)

    def set_published(self, slug: str, is_published: bool = True):
        print('Publishing...')
        if is_published:
            # TODO: PRETTY SURE IS_PUBLISHED SHOULD BE A URL PARAMETER SOMEWHERE. MAYBE A `STATE` ENDPOINT?
            res = requests.post(
                '{}/api/v1/posts/{}/publish'.format(self.base_url, slug),
                headers={'Authorization': self.api_key},
            )
        else:
            res = requests.post(
                '{}/api/v1/posts/{}/unpublish'.format(self.base_url, slug),
                headers={'Authorization': self.api_key},
            )
        print(res.json())

    def get_manifest(self) -> Manifest:
        res = requests.get(
            '{}/api/v1/posts'.format(self.base_url),
            headers={'Authorization': self.api_key},
        )
        if res.status_code == 401:
            raise ValueError('Couldn\'t access API: invalid authentication credentials')
        return Manifest(res.json())

    # TODO: SHOULD PROBABLY BE SOMEWHERE ELSE
    def apply_diff(self, diff: SiteDiff):
        for create_slug in diff.create_posts:
            self.create_post(create_slug)
        for delete_slug in diff.delete_posts:
            self.delete_post(delete_slug)
        for post_diff in diff.post_diffs:
            if post_diff.write_html:
                print('Uploading HTML')
                self.upload_html(post_diff.slug, post_diff.write_html)
            for upload in post_diff.write_images:
                print('Uploading {}'.format(upload))
                self.upload_image(post_diff.slug, upload)
            for delete in post_diff.delete_images:
                print('Deleting {}'.format(delete))
                self.delete_image(post_diff.slug, delete)
