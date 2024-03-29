from http import HTTPStatus
from typing import Any, Dict, Optional, Union, cast

import httpx

from ... import errors
from ...client import Client
from ...models.post_posts_post_id_content_multipart_data import (
    PostPostsPostIdContentMultipartData,
)
from ...types import Response


def _get_kwargs(
    post_id: int,
    *,
    client: Client,
    multipart_data: PostPostsPostIdContentMultipartData,
) -> Dict[str, Any]:
    url = "{}/posts/{post_id}/content".format(client.base_url, post_id=post_id)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    multipart_multipart_data = multipart_data.to_multipart()

    return {
        "method": "post",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "files": multipart_multipart_data,
    }


def _parse_response(
    *, client: Client, response: httpx.Response
) -> Optional[Union[Any, str]]:
    if response.status_code == HTTPStatus.NO_CONTENT:
        response_204 = cast(Any, None)
        return response_204
    if response.status_code == HTTPStatus.BAD_REQUEST:
        response_400 = cast(str, response.json())
        return response_400
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        response_401 = cast(Any, None)
        return response_401
    if response.status_code == HTTPStatus.FORBIDDEN:
        response_403 = cast(Any, None)
        return response_403
    if response.status_code == HTTPStatus.NOT_FOUND:
        response_404 = cast(Any, None)
        return response_404
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        response_500 = cast(Any, None)
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(f"Unexpected status code: {response.status_code}")
    else:
        return None


def _build_response(
    *, client: Client, response: httpx.Response
) -> Response[Union[Any, str]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    post_id: int,
    *,
    client: Client,
    multipart_data: PostPostsPostIdContentMultipartData,
) -> Response[Union[Any, str]]:
    """Upload the Markdown file of this post, overwriting whichever file had been there previously.

    Args:
        post_id (int):
        multipart_data (PostPostsPostIdContentMultipartData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, str]]
    """

    kwargs = _get_kwargs(
        post_id=post_id,
        client=client,
        multipart_data=multipart_data,
    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    post_id: int,
    *,
    client: Client,
    multipart_data: PostPostsPostIdContentMultipartData,
) -> Optional[Union[Any, str]]:
    """Upload the Markdown file of this post, overwriting whichever file had been there previously.

    Args:
        post_id (int):
        multipart_data (PostPostsPostIdContentMultipartData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, str]]
    """

    return sync_detailed(
        post_id=post_id,
        client=client,
        multipart_data=multipart_data,
    ).parsed


async def asyncio_detailed(
    post_id: int,
    *,
    client: Client,
    multipart_data: PostPostsPostIdContentMultipartData,
) -> Response[Union[Any, str]]:
    """Upload the Markdown file of this post, overwriting whichever file had been there previously.

    Args:
        post_id (int):
        multipart_data (PostPostsPostIdContentMultipartData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, str]]
    """

    kwargs = _get_kwargs(
        post_id=post_id,
        client=client,
        multipart_data=multipart_data,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    post_id: int,
    *,
    client: Client,
    multipart_data: PostPostsPostIdContentMultipartData,
) -> Optional[Union[Any, str]]:
    """Upload the Markdown file of this post, overwriting whichever file had been there previously.

    Args:
        post_id (int):
        multipart_data (PostPostsPostIdContentMultipartData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, str]]
    """

    return (
        await asyncio_detailed(
            post_id=post_id,
            client=client,
            multipart_data=multipart_data,
        )
    ).parsed
