import requests


meta = {
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
# print('Deleting...')
# res = requests.delete('http://localhost:5000/api/v1/posts/{}'.format(SLUG))
# print(res)

print('Creating...')
res = requests.post('http://localhost:5000/api/v1/posts/{}'.format(SLUG))
print(res)

print('Setting meta...')
res = requests.post('http://localhost:5000/api/v1/posts/{}/meta'.format(SLUG), json=meta)
print(res)

print('Uploading HTML...')
article_files = {'file': open('data/post.html', 'rb')}
res = requests.post('http://localhost:5000/api/v1/posts/{}/body'.format(SLUG), files=article_files)
print(res)

print('Uploading images')
images = {
    'gamla-stockholm.jpg': open('data/gamla-stockholm.jpg', 'rb'),
    'featured.jpg': open('data/featured.jpg', 'rb'),
}
for img in images.values():
    res = requests.post('http://localhost:5000/api/v1/posts/{}/images'.format(SLUG), files={'file': img})
    print(res)

print('Deleting images')
for filename in images:
    res = requests.delete('http://localhost:5000/api/v1/posts/{}/images/{}'.format(SLUG, filename))
    print(res)
