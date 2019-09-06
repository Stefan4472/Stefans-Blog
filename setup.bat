call venv\Scripts\activate
python -m flask init-db
python -m flask init-search-index
echo y|python add_post.py C:\Users\Stefan\Github\Blog-Content\project-overview-spaceships
echo y|python add_post.py C:\Users\Stefan\Github\Blog-Content\project-overview-c++-game
echo y|python add_post.py C:\Users\Stefan\Github\Blog-Content\inventory-systems
echo y|python add_post.py C:\Users\Stefan\Github\Blog-Content\tutorial-coding-a-texture-atlas
echo y|python add_post.py C:\Users\Stefan\Github\Blog-Content\when-o-of-n-squared-is-good-enough
set FLASK_APP=flaskr
set FLASK_ENV=development
python -m flask run