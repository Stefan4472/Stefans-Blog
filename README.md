# Stefans-Blog

A blog platform written in Python 3.6 using the [Flask](https://palletsprojects.com/p/flask/) framework. See it live at [www.stefanonsoftware.com](https://www.stefanonsoftware.com/).

## Sibling Projects

Along with this site, I'm working on two sibling projects:
- [simple-search](https://github.com/Stefan4472/simple-search-engine): A simple search engine written in Python. It's used in the search bar of the site.
- [site-analytics](https://github.com/Stefan4472/site-analytics): An API for collecting and analyzing website traffic. Also used in the site.

## Project Organization 

This repository contains code and templates, but no blog articles. My long-term goal is to make it 100% configurable, so that anyone _could_ use it to build their own blog.

Important directories:
- `flaskr`: the Flask code for the website, as well as static resources and templates.
- `imagecropper`: a Python module that provides a Tkinter GUI to crop an image to a specific size. This is used to create properly-sized thumbnails, for example.
- `sitemanager`: a Python module that provides a CLI to the blog's API.
- `renderer`: a Python module for rendering post Markdown into HTML.

Follow the setup instructions below to install the `imagecropper`, `sitemanager`, and `renderer` modules!

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

Install the `renderer` package:
```
pip install -e ./renderer
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

Posts are written in Markdown, which is rendered to HTML. I've found that I need some extra Markdown functionality--for example, rendering images as `<figure>` elements, or rendering code blocks. To make this possible, I created a little rendering program (the `renderer` module) that uses the `markdown2` library to render text to Markdown, and furthermore supports a few custom XML tags.

You can add a figure to your markdown using the custom `x-image` tag:
```
<x-image>
  <path>colorwheel.png</path>
  <caption>The RGB color wheel ([source](https://cdn.sparkfun.com/r/600-600/assets/learn_tutorials/7/1/0/TertiaryColorWheel_Chart.png))</caption>
  <alt>Image of the RGB color wheel</alt>
</x-image>
```

You can add a code block with [pygments](https://pygments.org/) syntax highlighting using the custom `<x-code>` tag:
```
# See the pygments languages documentation for a list of possible "language" arguments (https://pygments.org/languages/). Leave blank for no styling
<x-code language="python">
if __name__ == '__main__':
    print('Hello world')
</x-code>
```

## Ideas for Improvement

- Allow for "reference links", which add a "?ref=xxxxxx" key to the end of a URL. This way, we can track which clicks came from a specific LinkedIn post, for example.
- Use AJAX to display the "posts" page (load more posts dynamically), and provide Tag filters.
- Build a web interface for writing and managing posts