import datetime
import requests
from flask import request, current_app


def log_visit():
    # Get request IP address: https://stackoverflow.com/questions/3759981/get-ip-address-of-visitors-using-flask-for-python
    user_ip = request.environ.get(
        'HTTP_X_FORWARDED_FOR', request.environ['REMOTE_ADDR']
    )

    # Send data to the site-traffic analyzer
    params = {
        'url': request.path, 
        'ip_addr': user_ip,  
        'user_agent': request.environ['HTTP_USER_AGENT'],
        'secret': current_app.config['SECRET_VALS']['traffic_api_key'],
    }

    try:
        # requests.post('http://skussmaul.pythonanywhere.com/report_traffic', params=params)
        requests.post('http://127.0.0.1:5001/report_traffic', params=params)
    except requests.exceptions.ConnectionError as e:
        pass

    # Log to local file
    timestamp = datetime.datetime.now().strftime(r'%m-%d-%Y-%H:%M:%S:%f')[:-3]
    url = request.path
    # see https://stackoverflow.com/questions/3759981/get-ip-address-of-visitors-using-flask-for-python
    ip_addr = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ['REMOTE_ADDR'])
    user_agent = request.environ['HTTP_USER_AGENT']
    with open(current_app.config['SITE_LOG_PATH'], 'a') as log_file:
        log_file.write('{},{},{},{}\n'.format(timestamp, url, ip_addr, user_agent))