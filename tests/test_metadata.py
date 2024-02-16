import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Union

import pytest

from hatch_openzim.metadata import update

Metadata = Dict[str, Union[str, List[str]]]


@pytest.fixture
def dynamic_metadata() -> List[str]:
    return [
        "authors",
        "classifiers",
        "keywords",
        "license",
        "urls",
    ]


@pytest.fixture
def root_folder(tmp_path: Path) -> str:
    """
    Returns a "virtual" root folder with a "virtual" git config

    Git config comes from the tests/configs/gitconfig file

    This is necessary to ensure tests run always with the same git configuration file,
    to avoid variability coming from:
    - tests ran on plain files (not linked to any git repo)
    - tests ran on a repository fork (e.g myuser/hatch-openzim)
    - tests ran with a different remote (nothing forces main remote to be named origin)
    """
    git_folder = tmp_path / ".git"
    git_folder.mkdir()
    shutil.copy(
        Path(os.path.dirname(os.path.abspath(__file__))).parent
        / "tests/configs/gitconfig",
        git_folder / "config",
    )
    return str(tmp_path)


@pytest.fixture
def metadata(dynamic_metadata: List[str]) -> Metadata:
    return {
        "requires-python": ">=3.10,<3.12",
        "dynamic": dynamic_metadata,
    }


def test_metadata_nominal(metadata: Metadata, root_folder: str):
    update(
        root=root_folder,
        config={},
        metadata=metadata,
    )

    assert metadata["authors"] == [{"email": "dev@openzim.org", "name": "openZIM"}]
    assert metadata["classifiers"] == [
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ]
    assert metadata["keywords"] == ["openzim"]
    assert metadata["license"] == {"text": "GPL-3.0-or-later"}
    assert metadata["urls"] == {
        "Donate": "https://www.kiwix.org/en/support-us/",
        "Homepage": "https://github.com/openzim/hatch-openzim",
    }


@pytest.mark.parametrize(
    "metadata_key",
    [
        ("authors"),
        ("classifiers"),
        ("keywords"),
        ("license"),
        ("urls"),
    ],
)
def test_metadata_missing_dynamic(
    metadata: Metadata, metadata_key: str, root_folder: str
):
    assert isinstance(metadata["dynamic"], List)
    assert all(isinstance(item, str) for item in metadata["dynamic"])
    metadata["dynamic"].remove(metadata_key)
    with pytest.raises(
        Exception,
        match=f"'{metadata_key}' must be listed in 'project.dynamic' when using openzim"
        " metadata hook",
    ):
        update(
            root=root_folder,
            config={},
            metadata=metadata,
        )


@pytest.mark.parametrize(
    "metadata_key",
    [
        ("authors"),
        ("classifiers"),
        ("keywords"),
        ("license"),
        ("urls"),
    ],
)
def test_metadata_metadata_already_there(
    metadata: Metadata, metadata_key: str, root_folder: str
):
    metadata[metadata_key] = "some_value"
    with pytest.raises(
        Exception,
        match=f"'{metadata_key}' must not be listed in the 'project' table when using "
        "openzim metadata hook",
    ):
        update(
            root=root_folder,
            config={},
            metadata=metadata,
        )


@pytest.mark.parametrize(
    "metadata_key",
    [
        ("authors"),
        ("classifiers"),
        ("keywords"),
        ("license"),
        ("urls"),
    ],
)
def test_metadata_preserve_value(
    metadata: Metadata, metadata_key: str, root_folder: str
):
    metadata[metadata_key] = f"some_value_for_{metadata_key}"
    config: Dict[str, Any] = {}
    config[f"preserve-{metadata_key}"] = True
    update(
        root=root_folder,
        config=config,
        metadata=metadata,
    )
    assert metadata[metadata_key] == f"some_value_for_{metadata_key}"


def test_metadata_additional_keywords(metadata: Metadata, root_folder: str):
    config: Dict[str, Any] = {}
    config["additional-keywords"] = ["keyword1", "keyword2"]
    update(
        root=root_folder,
        config=config,
        metadata=metadata,
    )
    # we compare sets because order is not relevant
    assert set(metadata["keywords"]) == {"openzim", "keyword1", "keyword2"}


def test_metadata_additional_classifiers(metadata: Metadata, root_folder: str):
    config: Dict[str, Any] = {}
    config["additional-classifiers"] = [
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
    ]
    update(
        root=root_folder,
        config=config,
        metadata=metadata,
    )
    # we compare sets because order is not relevant
    assert set(metadata["classifiers"]) == {
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
    }


def test_metadata_additional_authors(metadata: Metadata, root_folder: str):
    config: Dict[str, Any] = {}
    config["additional-authors"] = [{"email": "someone@acme.org", "name": "Some One"}]
    update(
        root=root_folder,
        config=config,
        metadata=metadata,
    )
    # we compare sets because order is not relevant
    assert metadata["authors"] == [
        {"email": "dev@openzim.org", "name": "openZIM"},
        {"email": "someone@acme.org", "name": "Some One"},
    ]


@pytest.mark.parametrize(
    "organization, expected_result",
    [
        ("kiwix", "kiwix"),
        ("Kiwix", "kiwix"),
        ("openzim", "openzim"),
        ("openZIM", "openzim"),
        ("offspot", "kiwix"),
        ("unknown", "openzim"),
        (None, "openzim"),
    ],
)
def test_metadata_organization(
    organization: str, expected_result: str, metadata: Metadata, root_folder: str
):
    config: Dict[str, Any] = {}
    if organization:
        config["organization"] = organization
    update(
        root=root_folder,
        config=config,
        metadata=metadata,
    )
    if expected_result == "kiwix":
        assert metadata["authors"] == [{"email": "dev@kiwix.org", "name": "Kiwix"}]
        assert metadata["keywords"] == ["kiwix"]
    elif expected_result == "openzim":
        assert metadata["authors"] == [{"email": "dev@openzim.org", "name": "openZIM"}]
        assert metadata["keywords"] == ["openzim"]
    else:
        raise Exception(f"Unexpected expected result: {expected_result}")


def test_metadata_is_scraper(metadata: Metadata, root_folder: str):
    config: Dict[str, Any] = {}
    config["kind"] = "scraper"
    update(
        root=root_folder,
        config=config,
        metadata=metadata,
    )
    # we compare sets because order is not relevant
    assert set(metadata["keywords"]) == {"openzim", "offline", "zim"}
