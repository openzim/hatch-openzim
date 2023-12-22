from hatch_openzim.metadata import update

import pytest
from pathlib import Path
import os


@pytest.fixture
def dynamic_metadata():
    return [
        "authors",
        "classifiers",
        "keywords",
        "license",
        "urls",
    ]


@pytest.fixture
def metadata(dynamic_metadata):
    return {
        "requires-python": ">=3.10,<3.12",
        "dynamic": dynamic_metadata,
    }


def test_metadata_nominal(metadata, dynamic_metadata):
    update(
        root=str(Path(os.path.dirname(os.path.abspath(__file__))).parent),
        config={},
        metadata=metadata,
    )

    assert metadata["authors"] == [{"email": "dev@kiwix.org", "name": "Kiwix"}]
    assert metadata["classifiers"] == [
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ]
    assert metadata["keywords"] == ["kiwix"]
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
def test_metadata_missing_dynamic(metadata, metadata_key):
    metadata["dynamic"].remove(metadata_key)
    with pytest.raises(
        Exception,
        match=f"'{metadata_key}' must be listed in 'project.dynamic' when using openzim"
        " metadata hook",
    ):
        update(
            root=str(Path(os.path.dirname(os.path.abspath(__file__))).parent),
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
def test_metadata_metadata_already_there(metadata, metadata_key):
    metadata[metadata_key] = "some_value"
    with pytest.raises(
        Exception,
        match=f"'{metadata_key}' may not be listed in the 'project' table when using "
        "openzim metadata hook",
    ):
        update(
            root=str(Path(os.path.dirname(os.path.abspath(__file__))).parent),
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
def test_metadata_preserve_value(metadata, metadata_key):
    metadata[metadata_key] = f"some_value_for_{metadata_key}"
    config = {}
    config[f"preserve-{metadata_key}"] = True
    update(
        root=str(Path(os.path.dirname(os.path.abspath(__file__))).parent),
        config=config,
        metadata=metadata,
    )
    assert metadata[metadata_key] == f"some_value_for_{metadata_key}"


def test_metadata_additional_keywords(metadata, dynamic_metadata):
    config = {}
    config[f"additional-keywords"] = ["keyword1", "keyword2"]
    update(
        root=str(Path(os.path.dirname(os.path.abspath(__file__))).parent),
        config=config,
        metadata=metadata,
    )
    # we compare sets because order is not relevant
    assert set(metadata["keywords"]) == set(["kiwix", "keyword1", "keyword2"])


def test_metadata_is_scraper(metadata, dynamic_metadata):
    config = {}
    config[f"kind"] = "scraper"
    update(
        root=str(Path(os.path.dirname(os.path.abspath(__file__))).parent),
        config=config,
        metadata=metadata,
    )
    # we compare sets because order is not relevant
    assert set(metadata["keywords"]) == set(["kiwix", "offline", "zim"])
