import datetime
import requests
import functools
import typing
from flask import request, current_app


def log_visit():
    """Logs a visit to local file and notifies traffic API, if configured."""
    # Log to local file
    timestamp = datetime.datetime.now().strftime(r'%m-%d-%Y-%H:%M:%S:%f')[:-3]
    url = request.path
    # see https://stackoverflow.com/questions/3759981/get-ip-address-of-visitors-using-flask-for-python
    ip_addr = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ['REMOTE_ADDR'])
    user_agent = request.environ['HTTP_USER_AGENT']
    with open(current_app.config['LOG_PATH'], 'a') as log_file:
        log_file.write('{},{},{},{}\n'.format(timestamp, url, ip_addr, user_agent))

    # Send data to the site-traffic analyzer
    if current_app.config['TRAFFIC_API']:
        params = {
            'url': request.path,
            'ip_addr': ip_addr,
            'user_agent': request.environ['HTTP_USER_AGENT'],
            'secret': current_app.config['TRAFFIC_KEY'],
        }

        try:
            # requests.post('http://skussmaul.pythonanywhere.com/report_traffic', params=params)
            requests.post(current_app.config['TRAFFIC_API'], params=params)
        except requests.exceptions.ConnectionError as e:
            pass


def logged_visit(f: typing.Callable):
    """Decorator that logs the url being accessed. Simply calls `log_visit()`."""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        log_visit()
        return f(*args, **kwargs)
    return decorated_function
