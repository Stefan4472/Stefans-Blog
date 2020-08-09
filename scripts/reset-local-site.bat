call venv\Scripts\activate
set FLASK_APP=flaskr
set FLASK_ENV=development
python -m flask init_db
python -m flask init_search_index