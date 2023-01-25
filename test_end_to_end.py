import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import requests
from xprocess import ProcessStarter

# Path to where the test instance will be stored.
SITE_PATH = Path(__file__).parent / "end_to_end"
INSTANCE_PATH = SITE_PATH / "instance"
STATIC_PATH = SITE_PATH / "static"
# Credentials used for the test instance.
TEST_USERNAME = "test@test.com"
TEST_PASSWORD = "1234"
# Port on which to bring up the System Under Test.
PORT = 6777


@pytest.fixture
def sos_init():
    # TODO: this is actually overwriting os.environ, which we don't want. Deepcopy + pass as arg to subprocess.run. Then yield to sos_server
    env = os.environ
    env["FLASK_APP"] = "stefan-on-software/stefan_on_software"
    env["SECRET_KEY"] = "1234"
    env["INSTANCE_PATH"] = str(INSTANCE_PATH)
    env["STATIC_PATH"] = str(STATIC_PATH)

    os.makedirs(SITE_PATH, exist_ok=False)
    res_init = subprocess.run([sys.executable, "-m", "flask", "init_site"])
    if res_init.returncode:
        print(res_init.stdout)
        raise ValueError(f"Failed to initialize test instance: {res_init.stderr}")

    res_user = subprocess.run(
        [
            sys.executable,
            "-m",
            "flask",
            "add_user",
            "TEST_USER",
            TEST_USERNAME,
            f"--password={TEST_PASSWORD}",
        ]
    )
    if res_user.returncode:
        raise ValueError(f"Failed to create test user: {res_user.stderr}")

    yield

    print("Cleaning up")
    shutil.rmtree(SITE_PATH)


@pytest.fixture
def sos_server(xprocess, sos_init):
    class Starter(ProcessStarter):
        env = os.environ
        env["FLASK_APP"] = "stefan-on-software/stefan_on_software"
        # env['FLASK_ENV'] = 'development'
        env["SECRET_KEY"] = "1234"
        args = [sys.executable, "-m", "flask", "run", f"--port={PORT}"]
        # args = [sys.executable, '-m', 'pip', 'freeze']
        # args = [sys.executable, '-c', 'import stefan_on_software_api_client.api.files.post_files as api_post_files']
        timeout = 3
        # Here, we assume that our hypothetical process
        # will print the message "server has started"
        # once initialization is done
        pattern = f"Running on http://127.0.0.1:{PORT}"
        terminate_on_interrupt = True
        print(f"Bringing up test instance on http://127.0.0.1:{PORT}")

        def startup_check(self):
            return requests.get(f"http://127.0.0.1:{PORT}").status_code == 200

    # ensure process is running and return its logfile
    logfile = xprocess.ensure("sos_server", Starter)

    yield f"http://127.0.0.1:{PORT}"

    # clean up whole process tree afterwards
    xprocess.getinfo("sos_server").terminate()

    # Note: access log in .pytest_cache/d/.xprocess/sos_server/xprocess.log
    print(f"logfile contents in {logfile[1]}")
    # with open(logfile[1]) as r:
    #     print(r.read())


def test_end_to_end(sos_server):
    print(sos_server)

    # Create example post
    res_create = subprocess.run(
        [
            sys.executable,
            str(
                Path(__file__).parent
                / "stefan-on-software-api-client"
                / "bin"
                / "upload.py"
            ),
            str(Path(__file__).parent / "example-post"),
            f"--email={TEST_USERNAME}",
            f"--password={TEST_PASSWORD}",
            f"--host_url={sos_server}",
        ],
        capture_output=True,
    )
    print(res_create)
    if res_create.returncode:
        print(res_create.stdout)
        raise ValueError(f"Error creating post: {res_create.stderr}")
