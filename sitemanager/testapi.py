import requests


args = {
    "title": "How do Computer Graphics Work?",
    "byline": "If you're interested in game programming... or regular programming... or just computers in general, you should understand how computer graphics work. In this article we'll explain exactly that.",
    "tags": [
        "Tutorial",
        "GameDev",
        "Java",
        "IntroGameDev"
    ],
    "date": "09/18/17",
    "image": "colorwheel-featured.jpg",
    "thumbnail": "colorwheel-thumb.jpg",
    "banner": "colorwheel-banner.jpg"
}

SLUG = 'TEST_POST'
res = requests.post('http://localhost:5000/api/v1/posts/{}'.format(SLUG), json=args)
print(res)

article_files = {'file': open('data/post.html', 'rb')}
res = requests.post('http://localhost:5000/api/v1/posts/{}/body'.format(SLUG), files=article_files)
print(res)

images = {
    'im1': open('data/gamla-stockholm.jpg', 'rb'),
    'im2': open('data/featured.jpg', 'rb'),
}
res = requests.post('http://localhost:5000/api/v1/posts/{}/images'.format(SLUG), files=images)
print(res)
