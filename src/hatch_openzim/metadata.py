from pathlib import Path
from typing import Any, Dict

from hatch_openzim.utils import get_github_info, get_python_versions


def update(root: str, config: Dict[str, Any], metadata: Dict[str, Any]):
    """Update the project table's metadata."""

    # Check for absence of metadata we will set + presence in the dynamic property
    for metadata_key in ["urls", "authors", "keywords", "license", "classifiers"]:
        if config.get(f"preserve-{metadata_key}", False):
            # Do not check if we intend to preserve the value set manually
            continue

        if metadata_key in metadata:
            raise ValueError(
                f"'{metadata_key}' must not be listed in the 'project' table when using"
                " openzim metadata hook."
            )
        if metadata_key not in metadata.get("dynamic", []):
            raise ValueError(
                f"'{metadata_key}' must be listed in 'project.dynamic' when using "
                "openzim metadata hook."
            )

    github_info = get_github_info(git_config_path=Path(root) / ".git/config")

    organization = config.get("organization", github_info.organization)

    if not config.get("preserve-urls", False):
        metadata["urls"] = {
            "Donate": "https://www.kiwix.org/en/support-us/",
            "Homepage": github_info.homepage,
        }

    if not config.get("preserve-authors", False):
        if str(organization).lower() in ("kiwix", "offspot"):
            authors = [{"name": "Kiwix", "email": "dev@kiwix.org"}]
        else:
            authors = [{"name": "openZIM", "email": "dev@openzim.org"}]
        authors.extend(config.get("additional-authors", []))
        metadata["authors"] = authors

    if not config.get("preserve-keywords", False):
        if str(organization).lower() in ("kiwix", "offspot"):
            keywords = ["kiwix"]
        else:
            keywords = ["openzim"]
        if config.get("kind", "") == "scraper":
            keywords.extend(["zim", "offline"])
        keywords.extend(config.get("additional-keywords", []))
        metadata["keywords"] = keywords

    if not config.get("preserve-license", False):
        metadata["license"] = {"text": "GPL-3.0-or-later"}

    if not config.get("preserve-classifiers", False):
        classifiers = [
            "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)"
        ]
        for python_version in get_python_versions(metadata["requires-python"]):
            classifiers.append(f"Programming Language :: Python :: {python_version}")
        classifiers.extend(config.get("additional-classifiers", []))
        metadata["classifiers"] = classifiers
