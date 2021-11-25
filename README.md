# Stefans-Blog

A blog platform written in Python 3.6 using the [Flask](https://palletsprojects.com/p/flask/) framework. See it live at [www.stefanonsoftware.com](https://www.stefanonsoftware.com/).

**This project is a Work In Progress**. It is a hobby of mine that I revisit once or twice a year, and a lot of the code is waiting to be cleaned up and documented.

## Sibling Projects

Along with this site, I'm working on two sibling projects:
- [simple-search](https://github.com/Stefan4472/simple-search-engine): A simple search engine written in Python. It's used in the search bar of the site.
- [site-analytics](https://github.com/Stefan4472/site-analytics): An API for collecting and analyzing website traffic. Also used in the site.

## Project Organization 

This repository contains code and templates, but no blog articles. My long-term goal is to make it 100% configurable, so that anyone _could_ use it to build their own blog.

Important directories:
- `flaskr`: the Flask code for the website, as well as static resources and templates.
- `imagecropper`: a Python module that provides a Tkinter GUI to crop an image to a specific size. This is used to create properly-sized thumbnails, for example. Install with pip!
- `sitemanager`: a Python module that provides a CLI to the blog's API. Install with pip!

## Setup

Create a virtual environment and install the required packages:
```
python3 -m venv blogenv
call blogenv\Scripts\activate
pip install -r requirements.txt
```

Install the `imagecropper` package:
```
pip install -e ./imagecropper
```

Install the `sitemanager` package:
```
pip install -e ./sitemanager
```

Install my `simplesearch` package. It's not yet on pip, so you have to get it via Github:
```
git clone https://github.com/Stefan4472/simple-search-engine
cd simple-search-engine
pip install -e .
```

## Usage

To run the site, simply run Flask from the `flaskr` directory. The `python-dotenv` will use the `.flaskenv` config file to set environment variables for you.
```
cd flaskr 
flask run
```

To reset the site:
```
flask reset_site
```

## Custom Markdown Rendering

Posts are written in Markdown, which is rendered to HTML. I've found that I need some extra Markdown functionality--for example, rendering images as `<figure>` elements. To define a figure in your Markdown text, write:

```
<section type="image" path="colorwheel.png" caption="The RGB color wheel ([source](https://cdn.sparkfun.com/r/600-600/assets/learn_tutorials/7/1/0/TertiaryColorWheel_Chart.png))" alt="Image of the RGB color wheel"></section>
```

We have to define this as a "section" tag so that it is ignored by the Markdown renderer. The backend will first render the Markdown, and will then go through all `<section>` tags and generate `<figure>` tags out of them. This is a bit hacky but is the best I can do right now without modifying the `markdown2` library source code.

## Ideas for Improvement

- Allow for "reference links", which add a "?ref=xxxxxx" key to the end of a URL. This way, we can track which clicks came from a specific LinkedIn post, for example.
- Use AJAX to display the "posts" page (load more posts dynamically), and provide Tag filters.
- Build a web interface for writing and managing posts