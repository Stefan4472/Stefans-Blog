import requests
import pathlib
import dataclasses as dc
# Makes API requests
# TODO: FIND A GENERALIZED WAY TO SET BASE URL AND SLUG IN ONE PLACE
# TODO: EXCEPTIONS


@dc.dataclass
class ManagerService:
    base_url: str
    # api_key: str

    def create_post(self, slug: str):
        print('Creating...')
        res = requests.post('{}/api/v1/posts/{}'.format(self.base_url, slug))
        print(res)

    def delete_post(self, slug: str):
        print('Deleting...')
        res = requests.delete('{}/api/v1/posts/{}'.format(self.base_url, slug))
        print(res)

    def upload_html(self, slug: str, path: pathlib.Path):
        print('Uploading HTML...')
        res = requests.post(
            '{}/api/v1/posts/{}/body'.format(self.base_url, slug),
            files={'file': open(path, 'rb')},
        )
        print(res)

    def upload_image(self, slug: str, path: pathlib.Path):
        print('Uploading image {}'.format(path))
        with open(path, 'rb') as f:
            res = requests.post(
                '{}/api/v1/posts/{}/images'.format(self.base_url, slug),
                files={'file': f},
            )
            print(res)

    def delete_image(self, slug: str, filename: str):
        print('Deleting image')
        res = requests.delete('{}/api/v1/posts/{}/images/{}'.format(
            self.base_url,
            slug,
            filename,
        ))
        print(res)

    # TODO: META DATACLASS
    def set_meta(self, slug: str, meta: dict):
        print('Setting meta...')
        res = requests.post('{}/api/v1/posts/{}/meta'.format(self.base_url, slug), json=meta)
        print(res)

    def set_published(self, slug: str, is_published: bool = True):
        print('Publishing...')
        if is_published:
            # TODO: PRETTY SURE IS_PUBLISHED SHOULD BE A URL PARAMETER SOMEWHERE. MAYBE A `STATE` ENDPOINT?
            res = requests.post('{}/api/v1/posts/{}/publish'.format(self.base_url, slug))
        else:
            res = requests.post('{}/api/v1/posts/{}/unpublish'.format(self.base_url, slug))
        print(res.json())

    def get_manifest(self) -> dict:
        print('Getting manifest...')
        res = requests.get('{}/api/v1/posts'.format(self.base_url))
        print(res)
        return res.json()
