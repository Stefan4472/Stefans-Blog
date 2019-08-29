# Stefans-Blog
This project uses Python 3.

To setup the virtual environment:
>> cd Stefans-Blog
>> python -m venv venv
>> venv\Scripts\activate
>> pip install Flask

To run the site:
>> cd Stefans-Blog
>> venv\Scripts\activate
>> set FLASK_APP=flaskr
>> set FLASK_ENV=development
>> python -m flask run

To initialize/reset the database:
>> cd Stefans-Blog
>> python -m flask init-db