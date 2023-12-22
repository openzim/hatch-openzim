from typing import List

import pytest

from hatch_openzim.utils import get_github_project_homepage, get_python_versions


@pytest.fixture
def mock_check_output(mocker):
    return mocker.patch("subprocess.check_output", autospec=True)


@pytest.mark.parametrize(
    "path_to_repo, git_url, expected_homepage_url",
    [
        (
            "/path/https/repo",  # this must change between test cases due to lru_cache
            b"https://github.com/oneuser/onerepo.git\n",
            "https://github.com/oneuser/onerepo",
        ),
        (
            "/path/git/repo",  # this must change between test cases due to lru_cache
            b"git@github.com:oneuser/one-repo.git\n",
            "https://github.com/oneuser/one-repo",
        ),
    ],
)
def test_get_github_project_homepage_valid_url(
    mock_check_output, path_to_repo, git_url, expected_homepage_url
):
    mock_check_output.return_value = git_url
    result = get_github_project_homepage(path_to_repo)
    assert result == expected_homepage_url


@pytest.mark.parametrize(
    "path_to_repo, git_url",
    [
        (
            "/path/http/repo",
            b"http://github.com/oneuser/onerepo.git\n",
        ),
    ],
)
def test_get_github_project_homepage_invalid_url(
    mock_check_output, path_to_repo, git_url
):
    # Mock the subprocess.check_output call
    mock_check_output.return_value = git_url

    # Test the function with an invalid URL
    with pytest.raises(
        Exception, match=f"Unexpected remote url: {git_url.decode('utf-8').strip()}"
    ):
        get_github_project_homepage(path_to_repo)

    mock_check_output.assert_called_once()


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
        Exception, match=f"Multiple major versions is not supported for 3 and up"
    ):
        get_python_versions(requires_python)
