import requests
import pathlib
import flask
import dataclasses as dc
from manifest import Manifest, SiteDiff
from postconfig import PostConfig


@dc.dataclass
class ManagerService:
    base_url: str
    api_key: str

    def create_post(self, slug: str):
        res = requests.post(
            '{}/api/v1/posts/{}'.format(self.base_url, slug),
            headers={'Authorization': self.api_key},
        )
        self._check_response(res)

    def delete_post(self, slug: str):
        res = requests.delete(
            '{}/api/v1/posts/{}'.format(self.base_url, slug),
            headers={'Authorization': self.api_key},
        )
        self._check_response(res)

    def upload_html(self, slug: str, html: str):
        res = requests.post(
            '{}/api/v1/posts/{}/body'.format(self.base_url, slug),
            files={'file': ('post.html', html)},
            headers={'Authorization': self.api_key},
        )
        self._check_response(res)

    def upload_image(self, slug: str, path: pathlib.Path):
        with open(path, 'rb') as f:
            res = requests.post(
                '{}/api/v1/posts/{}/images'.format(self.base_url, slug),
                files={'file': f},
                headers={'Authorization': self.api_key},
            )
            self._check_response(res)

    def delete_image(self, slug: str, filename: str):
        url = '{}/api/v1/posts/{}/images/{}'.format(
            self.base_url,
            slug,
            filename,
        )
        res = requests.delete(
            url,
            headers={'Authorization': self.api_key},
        )
        self._check_response(res)

    def set_config(self, slug: str, config: PostConfig):
        res = requests.post(
            '{}/api/v1/posts/{}/config'.format(self.base_url, slug),
            json=config.to_json(),
            headers={'Authorization': self.api_key},
        )
        self._check_response(res)

    def get_manifest(self) -> Manifest:
        res = requests.get(
            '{}/api/v1/posts'.format(self.base_url),
            headers={'Authorization': self.api_key},
        )
        self._check_response(res)
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

    @staticmethod
    def _check_response(res: flask.Response):
        if res.status_code == 400:
            raise ValueError(res.text)
        elif res.status_code == 401:
            raise ValueError('Couldn\'t access API: invalid authentication credentials')
