from flask import request, current_app

def get_featured_posts(max_num=5):
    posts = []
    with open(current_app.config['FEATURED_POSTS_FILE'], 'r') as featured_file:
        for line in featured_file:
            line = line.lower().strip()
            # Ignore blank and commented lines
            if not line or line.startswith('#'):
                continue
            
            posts.append(line)
            if len(posts) >= max_num:
                break 
    return posts