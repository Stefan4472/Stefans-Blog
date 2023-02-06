"""
Uses pytest x-process to bring up a full system-under-test instance of the
flask server in a separate process. Then runs tests against that instance
using subprocesses.

Note: we use `sys.executable` (the path to the Python executable that's
running the script) in order to roughly simulate using the same virtual env
that's being used to run the script.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, Union

import pytest
import requests
from xprocess import ProcessStarter

# TODO: allow overriding certain options (e.g. PORT, SITE_PATH) via command line:
#  https://docs.pytest.org/en/7.1.x/example/simple.html#pass-different-values-to-a-test-function-depending-on-command-line-options
# Path of the project root.
ROOT_PATH = Path(__file__).parent
# Path to where the test instance will be stored.
SITE_PATH = ROOT_PATH / "end_to_end"
INSTANCE_PATH = SITE_PATH / "instance"
STATIC_PATH = SITE_PATH / "static"
# Path to the post to use for testing.
POST_PATH = ROOT_PATH / "example-post"
# Credentials used for the test instance.
TEST_USERNAME = "test@test.com"
TEST_PASSWORD = "1234"
# Port on which to bring up the System Under Test.
PORT = 6777


class TestInstance:
    def __init__(
        self,
        env: Dict,
        py_path: Path,
        root_path: Path,
        host_url: str,
        test_email: str,
        test_password: str,
    ):
        self._env = env
        self._py_path = py_path
        self._root_path = root_path
        self._host_url = host_url
        self._test_email = test_email
        self._test_password = test_password

    def bin_path(self) -> Path:
        """Get path to the 'bin' folder containing client scripts."""
        return self._root_path / "stefan-on-software-api-client" / "bin"

    def run_script(
        self, script_name: str, throw_error: bool = False, *script_args
    ) -> Union[subprocess.CompletedProcess, subprocess.CompletedProcess[bytes]]:
        print(f"Got script args {script_args}")
        res = subprocess.run(
            [
                self._py_path,
                str(self.bin_path() / script_name),
                *script_args,
                f"--email={self._test_email}",
                f"--password={self._test_password}",
                f"--host_url={self._host_url}",
            ],
            capture_output=True,
        )
        if res.returncode and throw_error:
            print(res.stdout)
            raise ValueError(
                f"Error executing script {script_name} with args {script_args}: {res.stderr}"
            )
        return res


@pytest.fixture
def sos_init() -> Dict:
    """
    Initializes the flask instance and registers a test user.
    Yields the environment variables to use when running the server.
    """
    # Set environment variables for test server instance.
    env = os.environ.copy()
    env["FLASK_APP"] = "stefan-on-software/stefan_on_software"
    env["SECRET_KEY"] = "1234"
    env["INSTANCE_PATH"] = str(INSTANCE_PATH)
    env["STATIC_PATH"] = str(STATIC_PATH)

    os.makedirs(SITE_PATH, exist_ok=False)
    res_init = subprocess.run([sys.executable, "-m", "flask", "init_site"], env=env)
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
        ],
        env=env,
    )
    if res_user.returncode:
        raise ValueError(f"Failed to create test user: {res_user.stderr}")

    yield env

    print("Cleaning up")
    shutil.rmtree(SITE_PATH)


@pytest.fixture
def sos_server(xprocess, sos_init) -> TestInstance:
    class Starter(ProcessStarter):
        # Use the environment variables provided by the sos_init fixture.
        env = sos_init
        args = [sys.executable, "-m", "flask", "run", f"--port={PORT}"]
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

    yield TestInstance(
        sos_init,
        Path(sys.executable),
        Path(__file__).parent,
        f"http://127.0.0.1:{PORT}",
        TEST_USERNAME,
        TEST_PASSWORD,
    )

    # clean up whole process tree afterwards
    xprocess.getinfo("sos_server").terminate()

    # Note: access log in .pytest_cache/d/.xprocess/sos_server/xprocess.log
    print(f"logfile contents in {logfile[1]}")
    # with open(logfile[1]) as r:
    #     print(r.read())


def test_end_to_end(sos_server: TestInstance):
    post_path = sos_server._root_path / "example-post"

    # Create example post.
    sos_server.run_script("upload.py", True, str(post_path))

    # TODO: we need to know the slug and ID of the created post
    # Publish the post
    sos_server.run_script(
        "manage.py", True, "publish-post", "1", "--send_email=False"
    )

    # Get the post at its URL
    res_published_post = requests.get(
        f"{sos_server._host_url}/post/gamedev-spritesheets"
    )
    assert res_published_post.status_code == 200
    assert b"<h1>How to Implement Spritesheets</h1>" in res_published_post.content

    # Update the post

    # Get the post at its URL and check that the change has been made

    # Feature the post

    # Verify

    # Unfeature the post

    # Verify

    # Unpublish

    # Verify

    # Delete

    # Verify
