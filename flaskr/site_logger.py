# really simple site visit logging
# space-separated: url timestamp IP-address
import datetime
from flask import request, current_app

def log_visit():
    timestamp = datetime.datetime.now()
    url = request.path
    # see https://stackoverflow.com/questions/3759981/get-ip-address-of-visitors-using-flask-for-python
    ip_addr = request.environ.get('HTTP_X_FORWARDED_FOR', \
              request.environ['REMOTE_ADDR'])
    with open(current_app.config['SITE_LOG_PATH'], 'a') as log_file:
        log_file.write('{} {} {}\n'.format(url, timestamp.strftime('%H:%M'), ip_addr))
