import re
import subprocess
from functools import lru_cache
from typing import List

from packaging.specifiers import SpecifierSet
from packaging.version import Version

REMOTE_REGEXP = re.compile(r"""^(?:git@|https:\/\/)github.com[:\/](.+)\/(.+).git$""")


@lru_cache(maxsize=None)
def get_github_project_homepage(root: str, remote: str = "origin") -> str:
    git_remote_url = (
        subprocess.check_output(
            ["git", "config", "--get", f"remote.{remote}.url"], cwd=root  # noqa: S607
        )
        .decode("utf-8")
        .strip()
    )
    match = REMOTE_REGEXP.match(git_remote_url)
    if not match:
        raise Exception(f"Unexpected remote url: {git_remote_url}")
    return f"https://github.com/{match.group(1)}/{match.group(2)}"


@lru_cache(maxsize=None)
def get_python_versions(requires_python: str) -> List[str]:
    """
    Returns the list of major and major.minor versions compatible with the specifier

    E.g. if requires_python is ">=3.10,<3.12", the result is "3", "3.10", "3.11"

    Nota: this does not work for requirements overlapping 3.x and 4.x, or later, because
     latest 3.x version is not yet known
    """
    specifier_set = SpecifierSet(requires_python)

    LAST_ONE_MINOR = 6
    LAST_TWO_MINOR = 7

    major_versions = []
    minor_versions = []
    for major in range(1, 10):  # this will work up to Python 10 ...
        major_added = False
        last_minor = 100  # this supposes we will never have Python x.100
        if major == 1:
            last_minor = LAST_ONE_MINOR
        elif major == 2:
            last_minor = LAST_TWO_MINOR
        for minor in range(last_minor + 1):
            if specifier_set.contains(Version(f"{major}.{minor}")):
                if not major_added:
                    if len(major_versions) > 0 and major >= 4:
                        raise Exception(
                            "Multiple major versions is not supported for 3 and up"
                        )
                    major_added = True
                    major_versions.append(f"{major}")
                minor_versions.append(f"{major}.{minor}")

    return major_versions + minor_versions
