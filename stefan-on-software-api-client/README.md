# stefan-on-software-api-client

A client library for accessing the StefanOnSoftware API and scripts for performing common operations. The vast majority of the code is generated automatically from an OpenAPI document using [openapi-python-client](https://github.com/openapi-generators/openapi-python-client).

## Using the API

First, create a client:

```python
from stefan_on_software_api_client.client_util import make_client

# Utility function that creates a client with HTTP Basic Authentication.
client = make_client("https://www.stefanonsoftware.com", "YOUR_EMAIL", "YOUR_PASSWORD")
```

Now call an endpoint from the `api` package and use models defined in the `models` package. See the scripts in `bin` for example usage. In general, every endpoint becomes a Python module with four functions:
    1. `sync`: Blocking request that returns parsed data (if successful) or `None`
    1. `sync_detailed`: Blocking request that always returns a `Request`, optionally with `parsed` set if the request was successful.
    1. `asyncio`: Like `sync` but async instead of blocking
    1. `asyncio_detailed`: Like `sync_detailed` but async instead of blocking

## Preparing a post

`python bin/prepare.py` provides a way to configure a post in a local directory for upload.
```shell
python bin/prepare.py ../example-post
```

## Uploading a post

`python bin/upload.py` performs the full process of creating a post on the website based on your local post. It will create the post, set its metadata, upload all of its images, add the specified tags, and upload its Markdown content.
```shell
python bin/upload.py ../example-post --email=YOUR_EMAIL --password=YOUR_PASSWORD --host_url=https://www.stefanonsoftware.com
```

## Updating a post

`python bin/update.py` provides a way to update the configuration and Markdown of an existing post and re-upload all of its images.
```shell
python bin/update.py ../example-post --email=YOUR_EMAIL --password=YOUR_PASSWORD --host_url=https://www.stefanonsoftware.com
```

## Managing the site

`python bin/manage.py` provides various utilities for managing existing posts in a site instance. For example:
```shell
python bin/manage.py create-tag "SLUG" "NAME" "DESCRIPTION" --email=YOU_EMAIL --password=YOUR PASSWORD" --host_url=https://www.stefanonsoftware.com"
```

Run `python bin/manage.py --help` for more information.