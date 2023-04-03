# Changelog

### January 15th, 2023
- "Official" StefanOnSoftware v0.1 release!
- API redesign and full documentation in an OpenApi spec.
- Major database schema changes accompanying the API changes.
- 60 unit tests (using the Flask test client), covering a large part of the API.
- Re-organized the project into four separately-installable packages.
- Lots of refactoring.
- [Read the accompanying blog post.](https://www.stefanonsoftware.com/post/stefan-on-software-v01)

### August 30th, 2022
- Implemented the StefanOnSoftware email newsletter.
- Fixed a bug in the post rendering process.

### January 6th, 2022
- Moved Markdown rendering to the backend (user now sends a Markdown file, rather than an HTML file). This is the first step towards in-site editing.
- Implemented custom XML tags in the Markdown rendering process. This makes it possible to incorporate custom HTML rendering for images and code segments.
- Implemented syntax highlighting for code segments with the Pygments library.
- Made post "title color" configurable to help avoid white-title-on-white-image problems.
- Implemented a brand-new Image API and completely reworked the Post API.
- Convert uploaded images to JPEG to save user bandwidth.

### November 1st, 2021
- Created a new API for site management (replaces the SFTP-sync method).
- Separated CLI-management tools from the website code.
- Lots of minor UI improvements.
- Improved package structure and use of .flaskenv for configuration.

### May 30th, 2021
- Migrated from SQLite to SQLAlchemy.
- Improved code quality, package structure, and Flask configuration.
- Pagination of results on the "Posts" page.

### March 7th, 2021
- Minor styling improvements of post widgets.
- Now using my [simple-search-engine](https://github.com/Stefan4472/simple-search-engine">simple-search-engine) project for search results.

### November 13th, 2020
- Implemented a blog "manifest" to track the posts and files belonging to a blog instance.
- On the backend, wrote code that uses the manifest to synchronize a local blog instance to a remote web server, e.g. to "push" to production. [Read the accompanying blog post.](https://www.stefanonsoftware.com/post/remote-synchronization-of-a-blog-instance)

### August 5th, 2020
- Wrote a Python/Tkinter program to make it much easier to crop and resize images to the desired standard sizes. Then went through <i>all</i> my posts and resized the images to look better. That was a lot of work!
- Implemented a "responsive" carousel to show Featured posts on the home page. The carousel uses Javascript to detect the window width and either show post information overlayed on top of the carousel, or beneath the carousel. For narrow screens (e.g., people viewing the site from their phones), the overlayed text looks really bad, so we instead show the post information below the carousel and hide the overlay. For large screens, we show the overlayed text, and hide the stuff beneath the carousel.
- Implemented "responsive" banners to show a different resolution image based on window width. The banner uses Javascript to detect the window width. On narrow screens, we show the post's "featured" image, which is currently set to 1000 x 540px. On wide screens, we show the post's "banner" image, which is currently set to 1000 x 300 px. This way, the banner looks pretty good on all screen sizes. [Read the accompanying blog post.](https://www.stefanonsoftware.com/post/javascript-for-responsive-web-design)

### September 17th, 2019
- Implemented "banner" and "thumbnail" for each post.
- Vastly improved the "devops" process of creating new posts and uploading them to the production server. Each post now has a "post.md" Markdown file, which contains its text, and a "post-meta.json" configuration file, which defines information such as the post's title, byline, official publish date, featured image, etc. The `manage_blog.py` script renders the post markdown, copies its images, and uses the metadata to add the post to the database. It then indexes the post and adds it to the search engine. Finally, if the user has turned the `--upload` setting on, the script uses SFTP to upload the new post HTML and images, along with the updated search index and database, to the production server.
- Small HTML/CSS styling improvements to center images and make captions look better.

### September 6th, 2019
- Modified a search engine I developed in order to use it for this site. This included implementing a way for the search index to save itself to a file (currently using JSON, because it's simple--although inefficient).
- Added search bar, with search results page.
- Added logging of visitor information (timestamp, url, IP address)--will be used for analysis in the future.
- Added carousel of "featured" posts.
- Now using the Python "RandomColor" library to generate tag colors randomly.

### September 3rd, 2019
- Created a fresh Flask install and followed the tutorial, setting things up the right way. "Doing it right". Everything is in a new repository now.

### March 13th, 2019
- Database re-write to really simplify things and make back-end improvements easier. The schema is now much simpler and the `Database` interface much easier to use.
- Added "Next" and "Previous" post links to each post. Just uses the post's index and adds or subtracts one. The next step will be to fetch the next/previous posts chronologically.
- Added the "recent posts" feature to the home page.
- Added the "Spaceships" site favicon.

### June 24th, 2018
- Rewrote a lot of the HTML to use Bootstrap.

### December 30th, 2017
- Got article tags working.
- Added "Posts" page, which shows all posts in chronological order.

### November 19th, 2017
- Significant back-end improvements to render Markdown post content to HTML via a new `site_manager.py` script. Post metadata is defined in a specific format at the top of each Markdown file.
- Much improved database schema and queries.

### October 28th, 2017
- Started using Flask and created Jinja templates.

### September 10th, 2017
- Created website using plain ol' HTML. Wrote several articles.
