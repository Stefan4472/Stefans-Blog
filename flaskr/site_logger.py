# really simple site visit logging
# space-separated: url timestamp IP-address
import datetime
from flask import request, current_app

def log_visit():
    # Format current time, accurate to the milliseconds (see https://stackoverflow.com/a/18406412)
    timestamp = datetime.datetime.now().strftime(r'%m-%d-%Y-%H:%M:%S:%f')[:-3]
    url = request.path
    # see https://stackoverflow.com/questions/3759981/get-ip-address-of-visitors-using-flask-for-python
    ip_addr = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ['REMOTE_ADDR'])
    user_agent = request.environ['HTTP_USER_AGENT']
    with open(current_app.config['SITE_LOG_PATH'], 'a') as log_file:
        log_file.write('{},{},{},{}\n'.format(timestamp, url, ip_addr, user_agent))
