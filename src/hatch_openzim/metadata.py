from pathlib import Path

from hatch_openzim.utils import get_github_project_homepage, get_python_versions


def update(root: str, config: dict, metadata: dict):
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

    if not config.get("preserve-urls", False):
        metadata["urls"] = {
            "Donate": "https://www.kiwix.org/en/support-us/",
            "Homepage": get_github_project_homepage(
                git_config_path=Path(root) / ".git/config"
            ),
        }

    if not config.get("preserve-authors", False):
        metadata["authors"] = [{"name": "Kiwix", "email": "dev@kiwix.org"}]

    if not config.get("preserve-keywords", False):
        keywords = ["kiwix"]
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
        metadata["classifiers"] = classifiers