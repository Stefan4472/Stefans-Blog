# Stefans-Blog

A blog platform written in Python 3.9 using the [Flask](https://palletsprojects.com/p/flask/) framework. See it live at [www.stefanonsoftware.com](https://www.stefanonsoftware.com/).

**This project is a Work In Progress**. It is a hobby of mine that I revisit once or twice a year, and a lot of the code is waiting to be cleaned up and documented.

## Project Organization 
This repository stores code only--it does not contain blog content.
```
- flaskr
  - search_engine: Pure-Python search engine implementation using QL scoring.
  - static: CSS and favicon. As articles are added to the blog, this folder will store post images and HTML.
  - templates/blog: Jinja2 HTML templates for the blog pages.
  - __init__.py: Flask initialization script.
  - blog.py: Code to serve URLs on the website.
  - database.py: Python Database class providing methods to execute SQL queries on the database.
  - featured_posts.py: Simple code which retrieves a list of "featured" posts. 
  - manage_blog.py: Command-line functions for adding posts to the site. Includes SFTP code for uploading the code to the site host.
  - posts_schema.sql: SQLite schema used for the post database.
  - site_logger.py: Simple code which logs site accesses.
- setup.bat: A Batch script for setting up a local Flask instance with several articles. I use this for a "single-step" build process.
```

## Setup
The following creates a virtual environment called `blogenv` and installs the required packages:
```
python3 -m venv blogenv
blogenv\Scripts\activate
pip install -r requirements.txt
```

## Usage
To run the site, activate the virtual environment and the run Flask:
```
set FLASK_APP=flaskr
set FLASK_ENV=development
python -m flask run
```

To reset the site:
```
python -m flask reset_site
```

To add a post:
```
python -m flask add_post POST_DIR
```
`POST_DIR` is an absolute or relative path to the post's directory.
Run ```python -m flask add_post help``` for instructions on using the options.

## Ideas for Improvement
- Allow for "reference links", which add a "?ref=xxxxxx" key to the end of a URL. This way, we can track which clicks came from a specific LinkedIn post, for example.
- Use AJAX to display the "posts" page (load more posts dynamically), and provide Tag filters.
- Build a web interface for adding posts