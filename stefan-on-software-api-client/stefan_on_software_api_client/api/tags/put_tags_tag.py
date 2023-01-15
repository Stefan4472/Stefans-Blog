from http import HTTPStatus
from typing import Any, Dict, Optional, Union, cast

import httpx

from ... import errors
from ...client import Client
from ...models.put_tags_tag_json_body import PutTagsTagJsonBody
from ...models.tag import Tag
from ...types import Response


def _get_kwargs(
    tag: str,
    *,
    client: Client,
    json_body: PutTagsTagJsonBody,
) -> Dict[str, Any]:
    url = "{}/tags/{tag}".format(client.base_url, tag=tag)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    json_json_body = json_body.to_dict()

    return {
        "method": "put",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "json": json_json_body,
    }


def _parse_response(
    *, client: Client, response: httpx.Response
) -> Optional[Union[Any, Tag, str]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = Tag.from_dict(response.json())

        return response_200
    if response.status_code == HTTPStatus.BAD_REQUEST:
        response_400 = cast(str, response.json())
        return response_400
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
) -> Response[Union[Any, Tag, str]]:
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
    json_body: PutTagsTagJsonBody,
) -> Response[Union[Any, Tag, str]]:
    """Update a tag

    Args:
        tag (str):
        json_body (PutTagsTagJsonBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Tag, str]]
    """

    kwargs = _get_kwargs(
        tag=tag,
        client=client,
        json_body=json_body,
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
    json_body: PutTagsTagJsonBody,
) -> Optional[Union[Any, Tag, str]]:
    """Update a tag

    Args:
        tag (str):
        json_body (PutTagsTagJsonBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Tag, str]]
    """

    return sync_detailed(
        tag=tag,
        client=client,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    tag: str,
    *,
    client: Client,
    json_body: PutTagsTagJsonBody,
) -> Response[Union[Any, Tag, str]]:
    """Update a tag

    Args:
        tag (str):
        json_body (PutTagsTagJsonBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Tag, str]]
    """

    kwargs = _get_kwargs(
        tag=tag,
        client=client,
        json_body=json_body,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    tag: str,
    *,
    client: Client,
    json_body: PutTagsTagJsonBody,
) -> Optional[Union[Any, Tag, str]]:
    """Update a tag

    Args:
        tag (str):
        json_body (PutTagsTagJsonBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Tag, str]]
    """

    return (
        await asyncio_detailed(
            tag=tag,
            client=client,
            json_body=json_body,
        )
    ).parsed
