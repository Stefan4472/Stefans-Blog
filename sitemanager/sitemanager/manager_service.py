import requests
import pathlib
import flask
import base64
import typing
from sitemanager.manifest import Manifest, SiteDiff
from sitemanager.postconfig import PostConfig
import sitemanager.util as util


class ManagerService:
    """Simple API layer."""
    def __init__(
            self,
            base_url: str,
            email: str,
            password: str,
    ):
        self.base_url = base_url
        self.email = email
        self.password = password

    def _make_headers(self):
        auth_string = f'{self.email}:{self.password}'
        auth_binary = base64.b64encode(auth_string.encode())
        return {'Authorization': 'Basic ' + auth_binary.decode()}

    def create_post(self, config: PostConfig, send_email: bool):
        config_json = config.to_json()
        config_json['send_email'] = send_email
        res = requests.post(
            f'{self.base_url}/api/v1/posts',
            json=config_json,
            headers=self._make_headers(),
        )
        self._check_response(res)

    def update_post(self, config: PostConfig):
        # Remove the `slug` param
        _json = config.to_json()
        _json.pop(util.KEY_SLUG)
        res = requests.put(
            f'{self.base_url}/api/v1/posts/{config.slug}',
            json=_json,
            headers=self._make_headers(),
        )
        self._check_response(res)

    def upload_markdown(self, slug: str, markdown: str):
        res = requests.put(
            f'{self.base_url}/api/v1/posts/{slug}/markdown',
            files={'file': ('post.md', markdown)},
            headers=self._make_headers(),
        )
        self._check_response(res)

    def delete_post(self, slug: str):
        res = requests.delete(
            f'{self.base_url}/api/v1/posts/{slug}',
            headers=self._make_headers(),
        )
        self._check_response(res)

    def upload_image(self, path: pathlib.Path) -> str:
        """Upload image at `path` and return the assigned on-server filename."""
        with open(path, 'rb') as f:
            res = requests.post(
                f'{self.base_url}/api/v1/images',
                files={'file': f},
                headers=self._make_headers(),
            )
            self._check_response(res)
            return res.json()['filename']

    def delete_image(self, filename: str):
        res = requests.delete(
            f'{self.base_url}/api/v1/images/{filename}',
            headers=self._make_headers(),
        )
        self._check_response(res)

    def get_manifest(self) -> Manifest:
        res = requests.get(
            f'{self.base_url}/api/v1/posts',
            headers=self._make_headers(),
        )
        self._check_response(res)
        return Manifest(res.json())

    def get_featured(self) -> typing.List[str]:
        res = requests.get(
            f'{self.base_url}/api/v1/featured',
            headers=self._make_headers(),
        )
        self._check_response(res)
        return res.json()

    def set_featured(self, slug: str, is_featured: bool):
        res = requests.patch(
            f'{self.base_url}/api/v1/posts/{slug}',
            headers=self._make_headers(),
            json={'feature': is_featured},
        )
        self._check_response(res)

    @staticmethod
    def _check_response(res: flask.Response):
        if res.status_code == 400:
            raise ValueError(res.text)
        elif res.status_code == 401:
            raise ValueError('Couldn\'t access API: invalid authentication credentials')
        elif res.status_code != 200:
            raise ValueError('Error: {}'.format(res.text))
