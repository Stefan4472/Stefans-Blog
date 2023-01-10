import re
import base64
import dataclasses as dc
from pathlib import Path
from typing import Dict, Optional
from sos_client.post_meta import PostMeta
from stefan_on_software_api_client.types import File as UploadFile, HTTPStatus
from stefan_on_software_api_client.client import Client
from stefan_on_software_api_client.models.post import Post
from stefan_on_software_api_client.models.post_files_multipart_data import PostFilesMultipartData
from stefan_on_software_api_client.models.file import File
import stefan_on_software_api_client.api.files.post_files as api_post_files
import stefan_on_software_api_client.api.posts.get_posts as api_get_posts
# TODO: merge in the contents of the other files into a single .py and add it to 'bin'?


@dc.dataclass
class LocalPost:
    """Simple struct to store information about a post on the local filesystem."""
    path: Path
    metadata: PostMeta

    @property
    def md_path(self) -> Path:
        return self.path / 'post.md'

    @property
    def meta_path(self) -> Path:
        return self.path / 'post-meta.json'


def load_post(path: Path) -> LocalPost:
    """Load and validate post that lives in the specified directory. May raise ValueError."""
    md_path = path / 'post.md'
    if not md_path.exists() or not md_path.is_file():
        raise ValueError(f'Could not find a post.md file in {path.absolute()}')
    meta_path = path / 'post-meta.json'
    if not meta_path.exists() or not meta_path.is_file():
        raise ValueError(f'Could not find a post-meta.json file in {path.absolute()}')
    try:
        post_meta = PostMeta.parse_from_file(meta_path)
    except ValueError as e:
        raise e
    return LocalPost(path, post_meta)


def generate_slug(string: str) -> str:
    """
    Generates a slug from the given string.

    Slugs are used to create readable urls.
    """
    string = string.replace(' ', '-').lower()
    # Remove any non letters, numbers, and non-dashes
    return re.sub(r'[^a-zA-Z0-9\-\+]+', '', string)


def make_client(host_url: str, email: str, password: str) -> Client:
    """
    Create a client with default configuration and basic auth configured.
    `host_url` is the base url of the host, e.g. http://localhost:5000. It must not end with '/'.
    """
    if host_url.endswith('/'):
        raise ValueError('host_url must not end with "/"')
    host_url += '/api/v1'
    return Client(
        host_url,
        headers=make_auth_headers(email, password),
        timeout=5,
        verify_ssl=False,
        raise_on_unexpected_status=True,
    )


def make_auth_headers(email: str, password: str) -> Dict:
    """Make headers for basic auth that will work with the test client."""
    auth_string = f'{email}:{password}'
    auth_binary = base64.b64encode(auth_string.encode())
    return {'Authorization': 'Basic ' + auth_binary.decode()}


def get_post_by_slug(client: Client, slug: str) -> Optional[Post]:
    # TODO: a better way to do this
    all_posts = api_get_posts.sync(client=client, limit=1000, offset=0)
    res = [post for post in all_posts if post.slug == slug]
    return res[0] if res else None


def upload_file(client: Client, file: UploadFile) -> File:
    res = api_post_files.sync_detailed(
        client=client,
        multipart_data=PostFilesMultipartData(file),
    )
    if res.status_code != HTTPStatus.OK and res.status_code != HTTPStatus.CREATED:
        raise ValueError(f'Failed with content={res.content}')
    return res.parsed
