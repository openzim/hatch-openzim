import os
from pathlib import Path

import pytest

from hatch_openzim.metadata import update


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


def test_metadata_nominal(metadata):
    update(
        root=str(Path(os.path.dirname(os.path.abspath(__file__))).parent),
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
        match=f"'{metadata_key}' must not be listed in the 'project' table when using "
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


def test_metadata_additional_keywords(metadata):
    config = {}
    config["additional-keywords"] = ["keyword1", "keyword2"]
    update(
        root=str(Path(os.path.dirname(os.path.abspath(__file__))).parent),
        config=config,
        metadata=metadata,
    )
    # we compare sets because order is not relevant
    assert set(metadata["keywords"]) == {"openzim", "keyword1", "keyword2"}


def test_metadata_additional_authors(metadata):
    config = {}
    config["additional-authors"] = [{"email": "someone@acme.org", "name": "Some One"}]
    update(
        root=str(Path(os.path.dirname(os.path.abspath(__file__))).parent),
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
def test_metadata_organization(organization, expected_result, metadata):
    config = {}
    if organization:
        config["organization"] = organization
    update(
        root=str(Path(os.path.dirname(os.path.abspath(__file__))).parent),
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


def test_metadata_is_scraper(metadata):
    config = {}
    config["kind"] = "scraper"
    update(
        root=str(Path(os.path.dirname(os.path.abspath(__file__))).parent),
        config=config,
        metadata=metadata,
    )
    # we compare sets because order is not relevant
    assert set(metadata["keywords"]) == {"openzim", "offline", "zim"}
