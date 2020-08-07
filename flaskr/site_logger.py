# really simple site visit logging
# space-separated: url timestamp IP-address
import datetime
from flask import request, current_app
import requests


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
    }
    try:
        requests.post('http://127.0.0.1:5001/report_traffic', params=params)
    except requests.exceptions.ConnectionError:
        pass
    # requests.post('http://sedu.pythonanywhere.com/report_traffic', params=params)
