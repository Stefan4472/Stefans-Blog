import datetime
import functools
import typing

import requests
from flask import current_app, request

from .site_config import ConfigKeys


def log_visit():
    """Logs a visit to local file and notifies traffic API, if configured."""
    timestamp = datetime.datetime.now().strftime(r"%m-%d-%Y-%H:%M:%S:%f")[:-3]
    url = request.path
    # https://stackoverflow.com/questions/3759981/get-ip-address-of-visitors-using-flask-for-python
    ip_address = request.environ.get(
        "HTTP_X_FORWARDED_FOR", request.environ["REMOTE_ADDR"]
    )
    user_agent = request.environ.get("HTTP_USER_AGENT", "")

    with open(current_app.config[ConfigKeys.TRAFFIC_LOG_PATH], "a") as log_file:
        log_file.write(f"{timestamp},{url},{ip_address},{user_agent}\n")

    if current_app.config[ConfigKeys.USE_SITE_ANALYTICS]:
        # Send data to site-analytics
        try:
            requests.post(
                current_app.config[ConfigKeys.SITE_ANALYTICS_URL],
                params={
                    "url": request.path,
                    "ip_addr": ip_address,
                    "user_agent": request.environ["HTTP_USER_AGENT"],
                    "secret": current_app.config[ConfigKeys.SITE_ANALYTICS_KEY],
                },
            )
        except requests.exceptions.ConnectionError:
            current_app.logger.error("Couldn't connect to SiteAnalytics")


def logged_visit(f: typing.Callable):
    """Decorator that logs the url being accessed. Simply calls `log_visit()`."""

    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        log_visit()
        return f(*args, **kwargs)

    return decorated_function
