# import sys  
# import re
# import os
import pathlib
# import shutil
# import click
# import pysftp
import typing
import datetime
# from flask import current_app, url_for
# from flask.cli import with_appcontext
from PIL import Image
# import json
# import markdown2 as md
# import randomcolor
# from flaskr.database import Database
# import flaskr.search_engine.index as index  # TODO: BETTER IMPORTS
# from flaskr.image_cropper.image_cropper import ImageCropper
# from flaskr.manifest import Manifest
# import tkinter as tk
# from tkinter.filedialog import askopenfilename


# Keys used in post-meta.json
KEY_TITLE = 'title'
KEY_BYLINE = 'byline'
KEY_SLUG = 'slug'
KEY_DATE = 'date'
KEY_TAGS = 'tags'
KEY_IMAGE = 'image'
KEY_BANNER = 'banner'
KEY_THUMBNAIL = 'thumbnail'

# # RandomColor object used to generate Tag colors
# COLOR_GENERATOR = randomcolor.RandomColor()

# # Prescribed featured-image size
# FEATURED_IMG_SIZE = (1000, 540)
# # Prescribed banner size
# BANNER_SIZE = (1000, 175) # (1928, 768)
# # Size of image thumbnails
# THUMBNAIL_SIZE = (400, 400)
# # The size that images in posts are resized to, by default
# DEFAULT_IMG_SIZE = (640, 480)

# # Generates a slug given a string.
# # Slugs are used to create readable urls
# def generate_slug(string):
#     string = string.replace(' ', '-').lower()
#     # Remove any non letters, numbers, and non-dashes
#     return re.sub(r'[^a-zA-Z0-9\-\+]+', '', string)

# def get_static_url(filepath):
#     return '{{{{ url_for(\'static\', filename=\'{}\') }}}}'.format(filepath)

# def generate_random_color():
#     return COLOR_GENERATOR.generate(luminosity='light', count=1)[0]

def resolve_directory_path(
        starting_dir: pathlib.Path,
        path: str,
) -> pathlib.Path:
    # Check the absolute path
    abs_path = pathlib.Path(path)
    if abs_path.is_dir():
        return abs_path
    # If that didn't work, check the relative path
    rel_path = pathlib.Path(starting_dir) / path
    if rel_path.is_dir():
        return rel_path
    # If that didn't work, raise error
    raise ValueError('Couldnt\'t find directory at absolute or relative path')

# def resolve_file_path(
#         starting_dir: pathlib.Path,
#         path: str,
# ) -> pathlib.Path:
#     # Check the absolute path
#     abs_path = pathlib.Path(path)
#     if abs_path.is_file():
#         return abs_path
#     # If that didn't work, check the relative path
#     rel_path = pathlib.Path(starting_dir) / path
#     if rel_path.is_file():
#         return rel_path
#     # If that didn't work, raise error
#     raise ValueError('Couldnt\'t find file at absolute or relative path')
        


#     # def render_markdown_file(
#     #         self,
#     #         filepath: pathlib.Path,
#     # ) -> str, typing.List[str]:
#     #     """Read the provided file and render to HTML. 

#     #     Returns the HTML as a string, and a list of all image sources
#     #     found in the document.
#     #     """
#     #     try:
#     #         post_markdown = \
#     #             open(filepath, 'r', encoding='utf-8', errors='strict') \
#     #                 .read() \
#     #                 .close()
#     #     except IOError:
#     #         raise ValueError(
#     #             'Could not read the post file ("{}")'.format(post_path))
#     #     return article_html, article_imgs = render_md_file(post_path, slug)


# # Takes the path to a Markdown file, read it, and renders it to HTML.
# # Returns (rendered HTML as a string, list of image sources found in <img> tags).
# # This function will render images as Bootstrap figures. 
# # TODO: EXPLAIN HOW TO ADD A CAPTION
# # TODO: THIS WHOLE FUNCTION SHOULD BE CLEANED UP, AND SHOULDN'T DEAL WITH 'IMG_SAVE_DIR'
# def render_md_file(file_path, img_save_dir):
#     # Regex used to match custom "[figure]" lines.
#     # Match 1: image path
#     # Match 2: optional image caption
#     figure_regex = re.compile(r'\[figure: ([^,\]]+)(?:, ([^\]]+))?]')
#     html_snippets = []
#     images = []
#     md_text = ''
#     last_match_index = -1

#     # print ('Reading file...')
#     with open(file_path, 'r', encoding='utf-8', errors='strict') as md_file:
#         md_text = md_file.read()
    
#     # Iterate through '[figure: ]' instances, which must be handled specially.
#     # Everything else can be rendered using the 'markdown' library.
#     for figure_match in re.finditer(figure_regex, md_text):
#         start = figure_match.start()
#         end = figure_match.end()
        
#         # Render the Markdown between the end of the last figure match and the start of
#         # this figure match (if it is non-whitespace)
#         if (start != last_match_index + 1) and md_text[last_match_index + 1 : start].strip():
#             rendered_html = md.markdown(md_text[last_match_index + 1 : start], extras=['fenced-code-blocks'])
#             html_snippets.append(rendered_html)

#         # Render the figure
#         img_path = figure_match.group(1)
#         img_caption = figure_match.group(2)
#         # print (img_path, img_caption)
#         img_url = get_static_url(img_save_dir + '/' + os.path.basename(img_path))  # TODO: CLEAN UP

#         # Render with caption
#         # TODO: HANDLE alt, and make this string a constant (?)
#         # TODO: ANY WAY TO MAKE THE BACKGROUND COLOR OF THE CAPTION GRAY, AND LIMIT IT TO THE WIDTH OF THE TEXT?
#         if img_caption:
#             rendered_html = \
# '''
# <figure class="figure text-center">
#     <img src="{}" class="figure-img img-fluid" alt="">
#     <figcaption class="figure-caption">{}</figcaption>
# </figure>

# '''.format(img_url, img_caption)
#         # Render without caption
#         else:
#             rendered_html = \
# '''
# <figure class="figure text-center">
#     <img src="{}" class="figure-img img-fluid" alt="">
# </figure>

# '''.format(img_url)
        
#         images.append(img_path)
#         html_snippets.append(rendered_html)
#         last_match_index = end

#     # Render the Markdown from the last figure match to the end of the file
#     if last_match_index != len(md_text):
#         rendered_html = md.markdown(md_text[last_match_index + 1 :], extras=['fenced-code-blocks'])
#         html_snippets.append(rendered_html)
#         #print (rendered_html)
    
#     return ''.join(html_snippets), images


# def copy_to_static(file_path, static_path):  # TODO: IMPROVE
#     # Make sure the file exists
#     if not (os.path.exists(file_path) and os.path.isfile(file_path)):
#         print ('ERROR: The image path "{}" is not a real file'.format(file_path))  # TODO: RAISE EXCEPTION
#         return

#     # Build destination path for the image
#     dest_path = os.path.join(static_path, os.path.basename(file_path))
#     # print (dest_path)
    
#     # Copy the image to the folder
#     shutil.copyfile(file_path, dest_path)


class PostImage:
    def __init__(
            self,
            image: Image.Image,
            path: pathlib.Path,
            sha1 = None,
    ):
        self.image = image
        self.path = path
        self.filename = path.name()
        self.sha1 = sha1


class PostData:
    def __init__(
            self,
            title: str,
            byline: str,
            slug: str,
            post_date: datetime.datetime,
            featured_img: PostImage,
            thumbnail_img: PostImage,
            banner_img: PostImage,
    ):
        self.title = title
        self.byline = byline
        self.slug = slug
        self.post_date = post_date
        self.featured_img = featured_img
        self.thumbnail_img = thumbnail_img
        self.banner_img = banner_img

class FileHash:
    def __init__(
            self,
            filepath: str,
            _hash: bytes,
            filesize: int,
    ):
        self.filepath = filepath
        self.hash = _hash
        self.filesize = filesize

class PostHashes:
    def __init__(
        self,
        html_hash: FileHash,
        featured_img_hash: FileHash,
        thumbnail_img_hash: FileHash,
        banner_img_hash: FileHash,
    ):
        self.html_hash = html_hash
        self.featured_img_hash = featured_img_hash
        self.thumbnail_img_hash = thumbnail_img_hash
        self.banner_img_hash = banner_img_hash
