hatch-openzim
=======

[![Code Quality Status](https://github.com/openzim/hatch-openzim/workflows/QA/badge.svg?query=branch%3Amain)](https://github.com/openzim/hatch-openzim/actions/workflows/QA.yml?query=branch%3Amain)
[![Tests Status](https://github.com/openzim/hatch-openzim/workflows/Tests/badge.svg?query=branch%3Amain)](https://github.com/openzim/hatch-openzim/actions/workflows/Tests.yml?query=branch%3Amain)
[![CodeFactor](https://www.codefactor.io/repository/github/openzim/hatch-openzim/badge)](https://www.codefactor.io/repository/github/openzim/hatch-openzim)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![codecov](https://codecov.io/gh/openzim/hatch-openzim/branch/main/graph/badge.svg)](https://codecov.io/gh/openzim/hatch-openzim)

This provides a [Hatch](https://pypi.org/project/hatch/)(ling) plugin for common openZIM operations:
- automatically populate common project metadatas
- install static files (e.g. external JS dependencies) at build time

This plugin intentionally has few dependencies, using the Python standard library whenever possible and hence limiting footprint to a minimum.

## Quick start

Assuming you have an openZIM project, you could use such a configuration in your `pyproject.toml`

```toml
# Use the hatchling build backend, with the hatch-openzim plugin.
[build-system]
requires = ["hatchling", "hatch-openzim"]
build-backend = "hatchling.build"

[project]
name = "MyAwesomeScraper"
requires-python = ">=3.11,<3.12"
description = "Awesome scraper"
readme = "README.md"

# These project metadatas are dynamic because they will be generated from hatch-openzim
# and version plugins.
dynamic = ["authors", "classifiers", "keywords", "license", "version", "urls"]

# Enable the hatch-openzim metadata hook to generate dependencies from addons manifests.
[tool.hatch.metadata.hooks.openzim]
additional-keywords = ["awesome"] # some additional 
kind = "scraper" # indicate this is a scraper, so that additional keywords are added

# Enable the hatch-openzim build hook to generate dependencies from addons manifests.
[tool.hatch.build.hooks.openzim]
toml-config = "openzim.toml" # optional location of the configuration file
```

## Metadata hook usage

The build hook configuration is done in a file named `openzim.toml` (if not customized)
 which must be placed in the root folder, next to your `pyproject.toml`.

### Configuration

| Variable | Required | Description |
|---|---|---|
| `preserve-authors` | N | Boolean indicating that we do not want to set `authors` metadata but use the ones of `pyproject.toml` |
| `preserve-classifiers` | N | Boolean indicating that we do not want to set `classifiers` metadata but use the ones of `pyproject.toml` |
| `preserve-keywords` | N | Boolean indicating that we do not want to set `keywords` metadata but use the ones of `pyproject.toml` |
| `preserve-license` | N | Boolean indicating that we do not want to set `license` metadata but use the one of `pyproject.toml` |
| `preserve-urls` | N | Boolean indicating that we do not want to set `urls` metadata but use the ones of `pyproject.toml` |
| `additional_keywords` | N | List of keywords that will be appended to the automatically added ones |
| `kind` | N | If set to `scraper`, scrapers keywords will be automatically added as well |

### Behavior

The metadata hook will set:

- `authors` to `[{"email": "dev@kiwix.org", "name": "Kiwix"}]`
- `classifiers` will contain:
  - `License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)`
  - all `Programming Language :: Python :: x` and `Programming Language :: Python :: x.y` matching the `required-versions`
- `keywords` will contain:
  - at least `kiwix`
  - if `kind` is `scraper`, ...
  - and `additional-keywords` passed in the configuration
- `license` to `{"text": "GPL-3.0-or-later"}``
- `urls` to
  - `"Donate": "https://www.kiwix.org/en/support-us/"`
  - `"Homepage": "https://github.com/openzim/hatch-openzim"`


## Build hook usage

The build hook configuration is done in a file named `openzim.toml` (if not customized)
 which must be placed in the root folder, next to your `pyproject.toml`.

### Configuration

| Variable | Required | Description |
|---|---|---|
| `toml-config` | N | Location of the configuration |

### Files installation

The build hook supports to download web resources at various location at build time.

To configure, this you first have to create a `files` section in the configuration and
declare its `config` configuration. Name of the section (`assets` in example below) is
free (do not forgot to escape it if you want to use special chars like `.` in the name).

```toml
[files.assets.config]
target_dir="src/hatch_openzim/templates/assets"
```

Configuration:

- `target_dir`: Base directory where all downloaded content will be placed

Once this section configuration is done, you will then declare multiple action. All
actions in a given section share the same base configuration

Three kinds of actions are supported:

- `get_file`: downloads a file to a location
- `extract_all`: extracts all content of a zip file to a location
- `extract_items`: extracts some items of a zip file to some locations

Each action is declared in its own TOML table. Action names are free.

```toml
[files.assets.actions.some_name]
action=...
```

### `get_file` action

This action downloads a file to a location.

- `action`: "get_file"
- `source`: URL of the online resource to download
- `target_file`: relative path to the file

You will find a sample below.

```toml
[files.assets.actions."jquery.min.js"]
action="get_file"
source="https://code.jquery.com/jquery-3.5.1.min.js"
target_file="jquery.min.js"
```

### `extract_all` action

This action downloads a ZIP and extracts it to a location. Some items in the Zip content
can be removed afterwards.

- `action`: "extract_all"
- `source`: URL of the online ZIP to download
- `target_dir`: relative path of the directory where ZIP content will be extracted
- `remove`: Optional - list of glob patterns of ZIP content to remove after extraction

You will find a sample below.

Nota:
- the ZIP is first saved to a temporary location before extraction, consuming some disk space

```toml
[files.assets.actions.chosen]
action="extract_all"
source="https://github.com/harvesthq/chosen/releases/download/v1.8.7/chosen_v1.8.7.zip"
target_dir="chosen"
remove=["docsupport", "chosen.proto.*", "*.html", "*.md"]
```

### `extract_items` action

This action extracts a ZIP to a temporary directory, and move selected items to some locations.
Some sub-items in the Zip content can be removed afterwards.

- `action`: "extract_all"
- `source`: URL of the online ZIP to download
- `zip_paths`: list of relative path in ZIP to select
- `target_paths`: relative path of the target directory where selected items will be moved
- `remove`: Optional - list of glob patterns of ZIP content to remove after extraction (must include the target paths)

Nota:
- the `zip_paths` and `target_paths` are match one-by-one, and must hence have the same length.
- the ZIP is first save to a temporary location before extraction, consuming some disk space
- all content is extracted before selected items are moved, and the rest is deleted

You will find a sample below.

```toml
[files.assets.actions.ogvjs]
action="extract_items"
source="https://github.com/brion/ogv.js/releases/download/1.8.9/ogvjs-1.8.9.zip"
zip_paths=["ogvjs-1.8.9"]
target_paths=["ogvjs"]
remove=["ogvjs/COPYING", "ogvjs/*.txt", "ogvjs/README.md"]
```

### Full sample

A full example with two distinct sections and three actions in total is below.

```toml
[files.assets.config]
target_dir="src/hatch_openzim/templates/assets"

[files.assets.actions."jquery.min.js"]
action="get_file"
source="https://code.jquery.com/jquery-3.5.1.min.js"
target_file="jquery.min.js"

[files.assets.actions.chosen]
action="extract_all"
source="https://github.com/harvesthq/chosen/releases/download/v1.8.7/chosen_v1.8.7.zip"
target_dir="chosen"
remove=["docsupport", "chosen.proto.*", "*.html", "*.md"]

[files.videos.config]
target_dir="src/hatch_openzim/templates/videos"

[files.videos.actions.ogvjs]
action="extract_items"
source="https://github.com/brion/ogv.js/releases/download/1.8.9/ogvjs-1.8.9.zip"
zip_paths=["ogvjs-1.8.9"]
target_paths=["ogvjs"]
remove=["ogvjs/COPYING", "ogvjs/*.txt", "ogvjs/README.md"]
```