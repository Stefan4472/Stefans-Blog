import requests
import pathlib
import flask
import typing
import dataclasses as dc
from sitemanager.manifest import Manifest, SiteDiff
from sitemanager.postconfig import PostConfig


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

    def upload_markdown(self, slug: str, markdown: str):
        res = requests.post(
            '{}/api/v1/posts/{}/body'.format(self.base_url, slug),
            files={'file': ('post.md', markdown)},
            headers={'Authorization': self.api_key},
        )
        self._check_response(res)

    def upload_image(self, slug: str, path: pathlib.Path) -> str:
        with open(path, 'rb') as f:
            res = requests.post(
                '{}/api/v1/posts/{}/images'.format(self.base_url, slug),
                files={'file': f},
                headers={'Authorization': self.api_key},
            )
            self._check_response(res)
            return res.text

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

    def get_featured(self) -> typing.List[str]:
        res = requests.get(
            '{}/api/v1/featured'.format(self.base_url),
            headers={'Authorization': self.api_key},
        )
        self._check_response(res)
        return res.json()

    def set_featured(self, slug: str, is_featured: bool):
        res = requests.post(
            '{}/api/v1/posts/{}/config'.format(self.base_url, slug),
            headers={'Authorization': self.api_key},
            json={'featured': is_featured},
        )
        self._check_response(res)

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

    def upload_image_new(self, path: pathlib.Path):
        with open(path, 'rb') as f:
            res = requests.post(
                f'{self.base_url}/api/v1/images',
                files={'file': f},
                headers={'Authorization': self.api_key},
            )
            self._check_response(res)
            return res.text.strip()

    def delete_image_new(self, filename: str):
        res = requests.delete(
            f'{self.base_url}/api/v1/images/{filename}',
            headers={'Authorization': self.api_key},
        )
        print(res)
        print(res.text)
        self._check_response(res)

    @staticmethod
    def _check_response(res: flask.Response):
        if res.status_code == 400:
            raise ValueError(res.text)
        elif res.status_code == 401:
            raise ValueError('Couldn\'t access API: invalid authentication credentials')
        elif res.status_code != 200:
            raise ValueError('Error: {}'.format(str(res)))
