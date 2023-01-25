# Stefans-Blog

A blogging website written in Python 3.9 using the [flask](https://palletsprojects.com/p/flask/) framework. Licensed under the MIT License. See it live at [www.stefanonsoftware.com](https://www.stefanonsoftware.com/).

## Features

- Modern, fully type-hinted Python3 syntax with [black](https://black.readthedocs.io), [isort](https://pycqa.github.io/isort/), and [pyflakes](https://pypi.org/project/pyflakes/) linting.
- Web UI rendered using [Jinja](https://jinja.palletsprojects.com/en/3.1.x/) templates and using [bootstrap4](https://getbootstrap.com/docs/4.0/getting-started/introduction/) for responsiveness.
- Backend [sqlite3](https://docs.python.org/3/library/sqlite3.html) database connection implemented using [sqlalchemy](https://www.sqlalchemy.org/).
- Custom Markdown rendering built on top of [markdown2](https://github.com/trentm/python-markdown2). Supports custom XML tags for images and colored code blocks powered by [pygments](https://pygments.org).
- Simple user accounts and permissions implemented using [flask-login](https://flask-login.readthedocs.io/en/latest/).
- RESTful API fully defined in [OpenAPI 3.0.0](https://swagger.io/specification/).
- Automatically-generated Python API client using [openapi-python-client](https://github.com/openapi-generators/openapi-python-client).
- API contract validation implemented using [marshmallow](https://marshmallow.readthedocs.io/en/stable/).
- Client-side [click](https://click.palletsprojects.com/en/8.1.x/) scripts that allow for uploading, updating, and managing blog posts on the site.
- Email list integration with [sendinblue](https://www.sendinblue.com/) using their [official Python SDK](https://github.com/sendinblue/APIv3-python-library).
- A simple Python GUI program for cropping images written with [tkinter](https://docs.python.org/3/library/tkinter.html).
- Decent unit test coverage with [pytest](https://pytest.org).

Along with this site, I'm also working on two sibling projects:
- [simple-search](https://github.com/Stefan4472/simple-search-engine): A simple search engine written in Python. It powers queries made via the website search bar.
- [site-analytics](https://github.com/Stefan4472/site-analytics): A simple web server that collects website traffic and makes it available for analysis.

This repository contains code and templates, but no blog articles. My long-term goal is to make it 100% configurable and extensible, so that anyone _could_ use it to build their own blog.

## Project Organization 

- `example-post`: an example post including Markdown text, images, and configuration.
- `stefan-on-software`: the website implementation. Contains the backend Flask code and the Jinja templates used to render the website.
- `stefan-on-software-api-client`: client code for the website's API. Most code is auto-generated based on `api.yaml`. See the `bin` directory for scripts to upload, update, and manage blog posts.
- `stefan-on-software-renderer`: code for rendering article Markdown into HTML. Supports custom XML elements. 
- `tk-image-cropper`: a Python GUI program used to crop images to a specified size.
- `api.yaml`: the website's API definition.

## Posts

The website does not (yet) have a graphical interface for writing posts. Therefore, posts are created on your local computer and uploaded to the website via the scripts in `stefan-on-software-api-client/bin`. Each post should have a separate directory that includes:
1. The Markdown content of the post in a file called `post.md`
2. The post configuration/metadata (e.g. Title, Byline, Tags) in a file called `post-meta.json`

See the provided example post (in the `example-post` directory) for more information.

## Setup

Upgrade pip (recommended) and install the required packages:
```
python -m pip install --upgrade pip
pip install -r requirements.txt
```

See the package-specific READMEs for more information.

## Linting

Code should be linted using [black](https://black.readthedocs.io/en/stable) and [isort](https://isort.readthedocs.io/en/latest/). Furthermore, before pushing, you should run [pyflakes](https://github.com/PyCQA/pyflakes) and ensure that there are no errors.
```shell
black . && isort . && pyflakes .
```

## Generating the API client

This project uses [openapi-python-client](https://github.com/openapi-generators/openapi-python-client) to automatically generate a Python client library based on the website's OpenAPI definition. To generate or update the client library, install [openapi-python-client](https://github.com/openapi-generators/openapi-python-client) in a separate virtual environment. Then, from the root directory of this project, run `openapi-python-client update --path api.yaml`.