import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Generator, List

import pytest

from hatch_openzim.utils import GithubInfo, get_github_info, get_python_versions


@pytest.fixture
def mock_git_config() -> Generator[Callable[[str, str], Any], None, None]:
    @contextmanager
    def _mock_git_config(git_origin_url: str, remote_name: str = "origin"):
        with tempfile.NamedTemporaryFile() as temp_file:
            git_config = Path(temp_file.name)
            git_config.write_text(
                f"""
[core]
        repositoryformatversion = 0
        filemode = true
        bare = false
        logallrefupdates = true
[remote "{remote_name}"]
        url = {git_origin_url}
        fetch = +refs/heads/*:refs/remotes/origin/*
"""
            )
            yield git_config

    yield _mock_git_config


@pytest.mark.parametrize(
    "git_url, expected_homepage_url, expected_organization, expected_repository",
    [
        (
            "https://github.com/oneuser/onerepo.git",
            "https://github.com/oneuser/onerepo",
            "oneuser",
            "onerepo",
        ),
        (
            "https://github.com/oneuser/onerepo",
            "https://github.com/oneuser/onerepo",
            "oneuser",
            "onerepo",
        ),
        (
            "git@github.com:oneuser/one-repo.git",
            "https://github.com/oneuser/one-repo",
            "oneuser",
            "one-repo",
        ),
    ],
)
def test_get_github_project_homepage_valid_url(
    mock_git_config: Callable[[str], Any],
    git_url: str,
    expected_homepage_url: str,
    expected_organization: str,
    expected_repository: str,
):
    with mock_git_config(git_url) as git_config_path:
        assert get_github_info(git_config_path=git_config_path) == GithubInfo(
            homepage=expected_homepage_url,
            organization=expected_organization,
            repository=expected_repository,
        )


def test_get_github_project_homepage_invalid_url(mock_git_config: Callable[[str], Any]):
    # Test the function with an invalid URL
    with mock_git_config("http://github.com/oneuser/onerepo.git") as git_config_path:
        assert get_github_info(git_config_path=git_config_path) == GithubInfo(
            homepage="https://www.kiwix.org", organization=None, repository=None
        )


def test_get_github_project_missing_git_config():
    # Test the function with an invalid URL
    assert get_github_info(git_config_path=Path("i_m_not_here.config")) == GithubInfo(
        homepage="https://www.kiwix.org", organization=None, repository=None
    )


def test_get_github_project_homepage_invalid_remote(
    mock_git_config: Callable[[str, str], Any],
):
    # Test the function with an invalid URL
    with mock_git_config(
        "https://github.com/oneuser/onerepo.git", "origin2"
    ) as git_config_path:
        assert get_github_info(git_config_path=git_config_path) == GithubInfo(
            homepage="https://www.kiwix.org", organization=None, repository=None
        )


@pytest.mark.parametrize(
    "requires_python, expected_versions",
    [
        (
            ">=3.1,<3.2",
            ["3", "3.1"],
        ),
        (
            ">=3.10,<3.12",
            ["3", "3.10", "3.11"],
        ),
        (
            ">=2.4,<3.1",
            ["2", "2.4", "2.5", "2.6", "2.7", "3", "3.0"],
        ),
    ],
)
def test_get_python_versions_ok(requires_python: str, expected_versions: List[str]):
    python_versions = get_python_versions(requires_python)
    # we compare sets because order does not matter
    assert set(python_versions) == set(expected_versions)
    # we compare length because we do not want duplicated values
    assert len(set(python_versions)) == len(python_versions)


@pytest.mark.parametrize(
    "requires_python",
    [
        (">=3.10,<4.1"),
        (">=3.6"),
    ],
)
def test_get_python_versions_ko(requires_python: str):
    with pytest.raises(
        Exception, match="Multiple major versions is not supported for 3 and up"
    ):
        get_python_versions(requires_python)
