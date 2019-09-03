call venv\Scripts\activate
python -m flask init-db
echo y|python add_post.py C:\Users\Stefan\Github\Blog-Webcode\sample_post
echo y|python add_post.py C:\Users\Stefan\Github\Blog-Content\project-overview-spaceships
set FLASK_APP=flaskr
set FLASK_ENV=development
python -m flask run