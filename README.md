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

Install the required packages:
```
pip install -r requirements.txt
```

There is a range of configuration values that can be set. See `flaskr/config.py` for more information. I recommend using a `.flaskenv` file and using absolute paths.

## Usage

To run the site, simply run Flask from the `flaskr` directory. The `python-dotenv` package will use the `.flaskenv` config file to set environment variables for you.
```
cd flaskr 
flask run
```

To reset the site's database:
```
flask reset_site
```

## Uploading a post

I've included an example post in the `example-post` directory. It provides a good example of how to write posts in Markdown with custom XML tags (described below) and how to configure a post via JSON (`post-meta.json`). To upload it to the site, first make sure the site is running (`flask run`, as per the instructions above). To upload it to the site, execute the following in a command prompt:
```
cd sitemanager
# This assumes SECRET_KEY='x123456', as set by default in `flaskr/.flaskenv`
python cli.py upload-post ..\example-post --host=http://127.0.0.1:5000 --key=x123456 --publish=true --allow_update=true 
# Optional: mark the post as "featured"
python cli.py set-featured gamedev-spritesheets --host=http://127.0.0.1:5000 --key=x123456 --featured=true
```

This command uses the `sitemanager` CLI to upload a post. The CLI communicates with the website's API to upload all files for you and configure the post properly. It will also open my `ImageCropper` program, allowing you to crop the post's featured image, banner and thumbnail to the correct sizes. Once finished, it will write the new (cropped) images to the file system and update the `post-meta.json`.

To see help information on the `upload-post` command, call `python cli.py upload-post --help`. The `upload-post` command also works on a live deployment--just set the `--host` and `--key` options properly. To see more available commands, run `python cli.py --help`.

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