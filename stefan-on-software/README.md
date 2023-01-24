# stefan-on-software

A blogging website implemented using Python [flask](https://palletsprojects.com/p/flask/).

## Setup

Install the `stefan_on_software` package. I recommend "editable" mode (`-e`) so that local changes you make take immediate effect:
```shell
pip install -e .
```

### Environment variables

Set your environment variables. The exact syntax depends on your shell program:
```shell
set FLASK_APP=stefan_on_software
set FLASK_ENV=development
set SECRET_KEY="{some secret key of your choice}"
```

**Recommended**: Alternatively, you can install [python-dotenv](https://pypi.org/project/python-dotenv/) and create a `.flaskenv` file containing the environment variables:
```
# Contents of your .flaskenv
FLASK_APP=stefan_on_software
FLASK_ENV=development
SECRET_KEY='x123456'
```

### Initialization

Initialize the database and all other necessary files:
```shell
python -m flask init_site
```

Create a user profile that you can use to login to the site and manage it via the API:
```shell
python -m flask add_user "{Your Name}" "{Your email address}" "{Your Password}"
```

### Configuration

Configuration is handled in `stefan_on_software/site_config.py`. You can set the following environment variables: (TODO: finish documentation)

- `SECRET_KEY`: secret key used for encryption of user passwords.
- `SQLALCHEMY_DATABASE_URI`: URI to the SQLite database. Must begin with 
- `TRAFFIC_LOG_PATH`:
- `SEARCH_INDEX_PATH`:
- `INSTANCE_PATH`:
- `STATIC_PATH`:
- `TESTING`:
- `USE_SITE_ANALYTICS`:
- `SITE_ANALYTICS_URL`:
- `SITE_ANALYTICS_KEY`:
- `USE_EMAIL_LIST`:
- `EMAIL_API_KEY`:
- `EMAIL_LIST_ID`:
- `SQLALCHEMY_TRACK_MODIFICATIONS`:
- `PAGINATE_POSTS_PER_PAGE`:

### Run

You can now start the server using `python -m flask run`, or simply `flask run`.

### Reset

You can delete the site using:
```shell
python -m flask delete_site
```