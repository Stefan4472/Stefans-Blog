# Stefans-Blog
A blog platform written in Python using the [Flask](https://palletsprojects.com/p/flask/) framework. See it live at [www.stefanonsoftware.com](www.stefanonsoftware.com).

This project isn't finished! I have plans for improvements, listed in the **Ideas for Improvement** section. 

Also keep in mind that this project has not been thoroughly documented. One of my TODOs is a big code cleanup.

## Project Organization 
This repository stores code only--it does not contain blog content.
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

## Virtual Environment
To setup the virtual environment:
```
python -m venv venv
venv\Scripts\activate
pip install Flask
pip install Pillow
pip install randomcolor
pip install pysftp
```

To run the site:
```
venv\Scripts\activate
set FLASK_APP=flaskr
set FLASK_ENV=development
python -m flask run
```

To initialize/reset the database:
```
python -m flask init_db
```

To initialize/reset the search index:
```
python -m flask init_search_index
```

To add a post:
```
python -m flask add_post POST_DIR
```
POST_DIR is an absolute or relative path to the post's directory.
Run ```python -m flask add_post help``` for instructions on using the options.

## Ideas for Improvement
- Use AJAX to display the "posts" page (load more posts dynamically), and provide Tag filters.
- Build a web interface for adding posts
- Provide tools for creating better thumbnails and banner images
- "LifeOfStefan": a special section of "daily life" posts that contain a single image and paragraph of text. These posts should be handled separately from the main blog posts, which are meant to be full articles.

Some links I need to read:
- http://exploreflask.com/en/latest/views.html
- https://stackoverflow.com/questions/36143283/pass-javascript-variable-to-flask-url-for
- https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xvi-full-text-search
- https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
- https://click.palletsprojects.com/en/5.x/quickstart/
- https://getbootstrap.com/docs/4.0/content/images/
- https://click.palletsprojects.com/en/7.x/options/
- https://pillow.readthedocs.io/en/3.1.x/reference/Image.html
- https://flask.palletsprojects.com/en/1.1.x/appcontext/

Markdown guide: https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet#headers