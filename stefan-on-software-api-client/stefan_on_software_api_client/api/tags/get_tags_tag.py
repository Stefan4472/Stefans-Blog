from http import HTTPStatus
from typing import Any, Dict, Optional, Union, cast

import httpx

from ... import errors
from ...client import Client
from ...models.tag import Tag
from ...types import Response


def _get_kwargs(
    tag: str,
    *,
    client: Client,
) -> Dict[str, Any]:
    url = "{}/tags/{tag}".format(client.base_url, tag=tag)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    return {
        "method": "get",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
    }


def _parse_response(
    *, client: Client, response: httpx.Response
) -> Optional[Union[Any, Tag]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = Tag.from_dict(response.json())

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
) -> Response[Union[Any, Tag]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    tag: str,
    *,
    client: Client,
) -> Response[Union[Any, Tag]]:
    """Get information about this tag

    Args:
        tag (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Tag]]
    """

    kwargs = _get_kwargs(
        tag=tag,
        client=client,
    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    tag: str,
    *,
    client: Client,
) -> Optional[Union[Any, Tag]]:
    """Get information about this tag

    Args:
        tag (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Tag]]
    """

    return sync_detailed(
        tag=tag,
        client=client,
    ).parsed


async def asyncio_detailed(
    tag: str,
    *,
    client: Client,
) -> Response[Union[Any, Tag]]:
    """Get information about this tag

    Args:
        tag (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Tag]]
    """

    kwargs = _get_kwargs(
        tag=tag,
        client=client,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    tag: str,
    *,
    client: Client,
) -> Optional[Union[Any, Tag]]:
    """Get information about this tag

    Args:
        tag (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Tag]]
    """

    return (
        await asyncio_detailed(
            tag=tag,
            client=client,
        )
    ).parsed
