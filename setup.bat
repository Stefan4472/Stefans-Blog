call venv\Scripts\activate
python -m flask init_db
python -m flask init_search_index
python -m flask add_post C:\Users\Stefan\Github\Blog-Content\project-overview-spaceships --quiet
python -m flask add_post C:\Users\Stefan\Github\Blog-Content\project-overview-c++-game --quiet
python -m flask add_post C:\Users\Stefan\Github\Blog-Content\inventory-systems --quiet
python -m flask add_post C:\Users\Stefan\Github\Blog-Content\tutorial-coding-a-texture-atlas --quiet
python -m flask add_post C:\Users\Stefan\Github\Blog-Content\when-o-of-n-squared-is-good-enough --quiet
set FLASK_APP=flaskr
set FLASK_ENV=development
python -m flask run