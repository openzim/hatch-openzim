import configparser
import re
from pathlib import Path
from typing import List, NamedTuple, Optional

from packaging.specifiers import SpecifierSet
from packaging.version import Version

from hatch_openzim.shared import logger

REMOTE_REGEXP = re.compile(
    r"""^(?:git@|https:\/\/)github.com[:\/](?P<organization>.*?)\/"""
    r"""(?P<repository>.*?)(?:.git)?$"""
)


class GithubInfo(NamedTuple):
    homepage: str
    organization: Optional[str]
    repository: Optional[str]


DEFAULT_GITHUB_INFO = GithubInfo(
    homepage="https://www.kiwix.org", organization=None, repository=None
)


def get_github_info(git_config_path: Path, remote: str = "origin") -> GithubInfo:
    if not git_config_path.exists() or not git_config_path.is_file():
        return DEFAULT_GITHUB_INFO

    try:
        config = configparser.ConfigParser()
        config.read(git_config_path)
        git_remote_url = config[f'remote "{remote}"']["url"]
        match = REMOTE_REGEXP.match(git_remote_url)
        if not match:
            raise Exception(f"Unexpected remote url: {git_remote_url}")
        return GithubInfo(
            homepage=f"https://github.com/{match.group('organization')}/"
            f"{match.group('repository')}",
            organization=match.group("organization"),
            repository=match.group("repository"),
        )
    except Exception as exc:
        logger.error("Failed to read Github URL", exc_info=exc)
        return DEFAULT_GITHUB_INFO


def get_python_versions(requires_python: str) -> List[str]:
    """
    Returns the list of major and major.minor versions compatible with the specifier

    E.g. if requires_python is ">=3.10,<3.12", the result is "3", "3.10", "3.11"

    Nota: this does not work for requirements overlapping 3.x and 4.x, or later, because
     latest 3.x version is not yet known
    """
    specifier_set = SpecifierSet(requires_python)

    last_py1_minor = 6
    last_py2_minor = 7

    major_versions: list[str] = []
    minor_versions: list[str] = []
    for major in range(1, 10):  # this will work up to Python 10 ...
        major_added = False
        last_minor = 100  # this supposes we will never have Python x.100
        if major == 1:
            last_minor = last_py1_minor
        elif major == 2:  # noqa: PLR2004
            last_minor = last_py2_minor
        for minor in range(last_minor + 1):
            if specifier_set.contains(Version(f"{major}.{minor}")):
                if not major_added:
                    if len(major_versions) > 0 and major >= 4:  # noqa: PLR2004
                        raise Exception(
                            "Multiple major versions is not supported for 3 and up"
                        )
                    major_added = True
                    major_versions.append(f"{major}")
                minor_versions.append(f"{major}.{minor}")

    return major_versions + minor_versions
