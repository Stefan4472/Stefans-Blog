"""A really simple and clunky integration tester."""
import subprocess
import sys
from pathlib import Path

import click


# TODO: figure out the best way to do this. Should be able to run without needing a live system so we can put this in a CI pipeline.
# TODO: go another step further and use HTML checking or Selenium?
@click.command()
@click.argument(
    "path", type=click.Path(exists=True, dir_okay=True, file_okay=False, path_type=Path)
)
@click.option("--email", required=True)
@click.password_option(required=True)
@click.option("--host_url", required=True)
def run_test(path: Path, email: str, password: str, host_url: str):
    """
    Test against a live system (e.g., localhost:5000).
    Will execute live commands, so this has the potential to create junk.
    """
    click.echo(f"Starting test of server at URL={host_url}")
    base_dir = Path(__file__).parent
    click.echo("Creating post...")
    # Running subprocess with sys.executable is a quick and dirty hack
    # that will kind of work to execute in the same virtual env.
    # res_test = subprocess.run([sys.executable, '-m', 'pip', 'freeze'], capture_output=True)
    # print(res_test)

    # Create example post
    res_create = subprocess.run(
        [
            sys.executable,
            str(base_dir / "upload.py"),
            str(path),
            f"--email={email}",
            f"--password={password}",
            f"--host_url={host_url}",
        ],
        capture_output=True,
    )
    if res_create.returncode:
        click.echo(f"Error creating post", err=True)
        click.echo(f"stdout={res_create.stdout}")
        click.echo(f"stderr={res_create.stderr}")
        sys.exit(1)
    # TODO: Here we could make sure that the post is not publicly-visible. However, that could also be done as a unit test.

    res_create = subprocess.run(
        [
            sys.executable,
            str(base_dir / "upload.py"),
            str(path),
            f"--email={email}",
            f"--password={password}",
            f"--host_url={host_url}",
        ],
        capture_output=True,
    )


if __name__ == "__main__":
    run_test()
