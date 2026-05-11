from pathlib import Path
from invoke import task
main_branch = "main"
dev_branch = "dev"


@task(name="preview", aliases=("rst",))
def preview(c):
    """Show a preview of the README file."""
    import sys
    rst_view = c.run(f"uvx restview --listen=8888 --browser --pypi-strict README.rst", asynchronous=True, out_stream=sys.stdout)
    print("Listening on http://localhost:8888/")
    rst_view.join()

@task
def clean(c):
    """Remove all artifacts."""
    patterns = ["build", "docs/build"]
    for pattern in patterns:
        c.run(f"rm -rf {pattern}")

@task
def minimum(c):
    """Check the minimum required python version for the project."""
    c.run("uvx vermin --no-parse-comments .")

@task
def test(c):
    """Run all tests under the tests directory."""
    c.run("uv pip install -r pyproject.toml --extra dev --extra test --extra doc")
    c.run("uv pip install -e .")
    c.run("uv run pytest tests")

@task
def release(c, version):
    """"""
    if version not in ["minor", "major", "patch"]:
        print("Version can be either major, minor or patch.")
        return

    import tomllib
    data = tomllib.loads(Path("pyproject.toml").read_text())
    old_version = data.get("project", {}).get("version")
    _major, _minor, _patch = [int(part) for part in old_version.split(".")]

    if version == "patch":
        _patch = _patch + 1
    elif version == "minor":
        _minor = _minor + 1
        _patch = 0
    elif version == "major":
        _major = _major + 1
        _minor = 0
        _patch = 0

    c.run(f"git checkout {dev_branch}") # Just to fail early in case the dev branch does not exist
    c.run(f"git checkout -b release-{_major}.{_minor}.{_patch} {dev_branch}")
    c.run(f"sed -i 's/\"{old_version}\"/\"{_major}.{_minor}.{_patch}\"/g' pyproject.toml")
    c.run(f"sed -i 's/\"{old_version}\"/\"{_major}.{_minor}.{_patch}\"/g' docs/conf.py")
    print(f"Update the readme for version {_major}.{_minor}.{_patch}.")
    print(f"Run 'uv lock --upgrade'.")
    input("Press enter when ready.")
    c.run(f"git add -u")
    c.run(f'git commit -m "Update changelog version {_major}.{_minor}.{_patch}"')
    c.run(f"git push --set-upstream origin release-{_major}.{_minor}.{_patch}")
    c.run(f"git checkout {main_branch}")
    c.run(f"git pull")
    c.run(f"git merge --no-ff release-{_major}.{_minor}.{_patch}")
    c.run(f'git tag -a {_major}.{_minor}.{_patch} -m "Release {_major}.{_minor}.{_patch}"')
    c.run(f"git push")
    c.run(f"git checkout {dev_branch}")
    c.run(f"git merge --no-ff release-{_major}.{_minor}.{_patch}")
    c.run(f"git push")
    c.run(f"git branch -d release-{_major}.{_minor}.{_patch}")
    c.run(f"git push origin --tags")
