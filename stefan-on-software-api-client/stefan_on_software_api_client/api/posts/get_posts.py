from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union, cast

import httpx

from ... import errors
from ...client import Client
from ...models.post import Post
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    client: Client,
    is_featured: Union[Unset, None, bool] = UNSET,
    is_published: Union[Unset, None, bool] = UNSET,
    limit: int,
    offset: int,
) -> Dict[str, Any]:
    url = "{}/posts".format(client.base_url)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    params: Dict[str, Any] = {}
    params["is_featured"] = is_featured

    params["is_published"] = is_published

    params["limit"] = limit

    params["offset"] = offset

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    return {
        "method": "get",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(
    *, client: Client, response: httpx.Response
) -> Optional[Union[Any, List["Post"]]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = Post.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        response_401 = cast(Any, None)
        return response_401
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
) -> Response[Union[Any, List["Post"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Client,
    is_featured: Union[Unset, None, bool] = UNSET,
    is_published: Union[Unset, None, bool] = UNSET,
    limit: int,
    offset: int,
) -> Response[Union[Any, List["Post"]]]:
    """Get post information, applying optional filters and paging.

    Args:
        is_featured (Union[Unset, None, bool]):
        is_published (Union[Unset, None, bool]):
        limit (int):
        offset (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, List['Post']]]
    """

    kwargs = _get_kwargs(
        client=client,
        is_featured=is_featured,
        is_published=is_published,
        limit=limit,
        offset=offset,
    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Client,
    is_featured: Union[Unset, None, bool] = UNSET,
    is_published: Union[Unset, None, bool] = UNSET,
    limit: int,
    offset: int,
) -> Optional[Union[Any, List["Post"]]]:
    """Get post information, applying optional filters and paging.

    Args:
        is_featured (Union[Unset, None, bool]):
        is_published (Union[Unset, None, bool]):
        limit (int):
        offset (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, List['Post']]]
    """

    return sync_detailed(
        client=client,
        is_featured=is_featured,
        is_published=is_published,
        limit=limit,
        offset=offset,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    is_featured: Union[Unset, None, bool] = UNSET,
    is_published: Union[Unset, None, bool] = UNSET,
    limit: int,
    offset: int,
) -> Response[Union[Any, List["Post"]]]:
    """Get post information, applying optional filters and paging.

    Args:
        is_featured (Union[Unset, None, bool]):
        is_published (Union[Unset, None, bool]):
        limit (int):
        offset (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, List['Post']]]
    """

    kwargs = _get_kwargs(
        client=client,
        is_featured=is_featured,
        is_published=is_published,
        limit=limit,
        offset=offset,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Client,
    is_featured: Union[Unset, None, bool] = UNSET,
    is_published: Union[Unset, None, bool] = UNSET,
    limit: int,
    offset: int,
) -> Optional[Union[Any, List["Post"]]]:
    """Get post information, applying optional filters and paging.

    Args:
        is_featured (Union[Unset, None, bool]):
        is_published (Union[Unset, None, bool]):
        limit (int):
        offset (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, List['Post']]]
    """

    return (
        await asyncio_detailed(
            client=client,
            is_featured=is_featured,
            is_published=is_published,
            limit=limit,
            offset=offset,
        )
    ).parsed
