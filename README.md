# Stefans-Blog
This project uses Python 3.

To setup the virtual environment:
```
cd Stefans-Blog
python -m venv venv
venv\Scripts\activate
pip install Flask
pip install Pillow
pip install randomcolor
pip install pysftp
```

To run the site:
```
cd Stefans-Blog
venv\Scripts\activate
set FLASK_APP=flaskr
set FLASK_ENV=development
python -m flask run
```

To initialize/reset the database:
```
cd Stefans-Blog
python -m flask init-db
```

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