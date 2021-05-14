from flask_sqlalchemy import SQLAlchemy


# This needs to be in a separate file to avoid circular imports
# See https://stackoverflow.com/a/23400668
db = SQLAlchemy()
