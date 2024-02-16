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

hatch-openzim adheres to openZIM's [Contribution Guidelines](https://github.com/openzim/overview/wiki/Contributing).

hatch-openzim has implemented openZIM's [Python bootstrap, conventions and policies](https://github.com/openzim/_python-bootstrap/docs/Policy.md) **v1.0.0**.

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

# Enable the hatch-openzim metadata hook to generate default openZIM metadata.
[tool.hatch.metadata.hooks.openzim-metadata]
additional-keywords = ["awesome"] # some additional keywords
kind = "scraper" # indicate this is a scraper, so that additional keywords are added

# Additional author #1
[[tool.hatch.metadata.hooks.openzim-metadata.additional-authors]]
name="Bob"
email="bob@acme.com"

# Additional author #2
[[tool.hatch.metadata.hooks.openzim-metadata.additional-authors]]
name="Alice"
email="alice@acme.com"

# Enable the hatch-openzim build hook to install files (e.g. JS libs) at build time.
[tool.hatch.build.hooks.openzim-build]
toml-config = "openzim.toml" # optional location of the configuration file
dependencies = [ "zimscraperlib==3.1.0" ] # optional dependencies needed for file installations
```

NOTA: the `dependencies` attribute is not specific to our hook(s), it is a generic [hatch(ling) feature](https://hatch.pypa.io/1.9/config/build/#dependencies_1).

## Metadata hook usage

### Configuration (in `pyproject.toml`)

| Variable | Required | Description |
|---|---|---|
| `additional-authors` | N | List of authors that will be appended to the automatic one |
| `additional-classifiers` | N | List of classifiers that will be appended to the automatic ones |
| `additional-keywords` | N | List of keywords that will be appended to the automatic ones |
| `kind` | N | If set to `scraper`, scrapers keywords will be automatically added as well |
| `organization` | N | Override organization (otherwise detected from Github repository to set author and keyword appropriately). Case-insentive. Supported values are `openzim`, `kiwix` and `offspot` |
| `preserve-authors` | N | Boolean indicating that we do not want to set `authors` metadata but use the ones of `pyproject.toml` |
| `preserve-classifiers` | N | Boolean indicating that we do not want to set `classifiers` metadata but use the ones of `pyproject.toml` |
| `preserve-keywords` | N | Boolean indicating that we do not want to set `keywords` metadata but use the ones of `pyproject.toml` |
| `preserve-license` | N | Boolean indicating that we do not want to set `license` metadata but use the one of `pyproject.toml` |
| `preserve-urls` | N | Boolean indicating that we do not want to set `urls` metadata but use the ones of `pyproject.toml` |

### Behavior

The metadata hook will set:

- `authors` to `[{"email": "dev@kiwix.org", "name": "Kiwix"}]`
- `classifiers` will contain:
  - `License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)`
  - all `Programming Language :: Python :: x` and `Programming Language :: Python :: x.y` matching the `required-versions`
- `keywords` will contain:
  - at least `kiwix`
  - if `kind` is `scraper`, it will add `zim` and `offline`
  - and `additional-keywords` passed in the configuration
- `license` to `{"text": "GPL-3.0-or-later"}`
- `urls` to
  - `Donate`: `https://www.kiwix.org/en/support-us/`
  - `Homepage`: Github repository URL (e.g. `https://github.com/openzim/hatch-openzim`) if code is a git clone, otherwise `https://www.kiwix.org`


## Build hook usage

### High-level configuration (in `pyproject.toml`)

| Variable | Required | Description |
|---|---|---|
| `toml-config` | N | Location of the configuration, default to `openzim.toml` |

### Details configuration (in `openzim.toml`)

The build hook detailed configuration is done in a TOML file named `openzim.toml` (if not customized
 via `toml-config`, see above). This file must be placed your project root folder, next to your
  `pyproject.toml`.

The build hook supports to download web resources at various location at build time.

To configure, this you first have to create a `files` section in the `openzim.toml` configuration
and declare its `config` configuration. Name of the section (`assets` in example below) is
free (do not forgot to escape it if you want to use special chars like `.` in the name).

```toml
[files.assets.config]
target_dir="src/hatch_openzim/templates/assets"
execute_after=[
    "touch somewhere/something.txt"
]
```

| Variable | Required | Description |
|---|---|---|
| `target_dir` | Y | Base directory where all downloaded content will be placed |
| `execute_after` | N | List of shell commands to execute once all actions (see below) have been executed; actions are executed with `target_dir` as current working directory |

**Important:** The `execute_after` commands are **always** executed, no matter how many action are
 present or how many actions have been ignored (see below for details about why an action might be ignored).

Nota: The example `execute_after` command (`touch`) is not representative of what you would usually do ^^

Once this section configuration is done, you will then declare multiple actions. All
actions in a given section share the same base configuration declared above.

Three kinds of actions are supported:

- `get_file`: downloads a file to a location
- `extract_all`: extracts all content of a zip file to a location
- `extract_items`: extracts some items of a zip file to some locations

Each action is declared in its own TOML table. Action names are free.

```toml
[files.assets.actions.some_name]
action=...
```

### `get_file` action configuration (in `openzim.toml`)

This action downloads a file to a location.

**Important:** If `target_file` is already present, the action is not executed, it is simply ignored.

| Variable | Required | Description |
|---|---|---|
| `action` | Y | Must be "get_file" |
| `source`| Y | URL of the online resource to download |
| `target_file` | Y | Relative path to the file target location, relative to the section `target_dir` |
| `execute_after` | N | List of shell commands to execute once file installation is completed; actions are executed with the section `target_dir` as current working directory |

You will find a sample below.

```toml
[files.assets.actions."jquery.min.js"]
action="get_file"
source="https://code.jquery.com/jquery-3.5.1.min.js"
target_file="jquery.min.js"
```

### `extract_all` action configuration (in `openzim.toml`)

This action downloads a ZIP and extracts it to a location. Some items in the Zip content
can be removed afterwards.

**Important:** If `target_dir` is already present, the action is not executed, it is simply ignored.

| Variable | Required | Description |
|---|---|---|
| `action` | Y | Must be "extract_all" |
| `source` | Y | URL of the online ZIP to download |
| `target_dir` | Y | Relative path of the directory where ZIP content will be extracted, relative to the section `target_dir` |
| `remove` | N | List of glob patterns of ZIP content to remove after extraction (relative to action `target_dir`) |
| `execute_after` | N | List of shell commands to execute once files extraction is completed; actions are executed with the section `target_dir` as current working directory |


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

### `extract_items` action configuration (in `openzim.toml`)

This action extracts a ZIP to a temporary directory, and move selected items to some locations.
Some sub-items in the Zip content can be removed afterwards.

**Important:** If any `target_paths` is already present, the action is not executed, it is simply ignored.

| Variable | Required | Description |
|---|---|---|
| `action`| Y | Must be "extract_all" |
| `source`| Y | URL of the online ZIP to download |
| `zip_paths` | Y | List of relative path in ZIP to select |
| `target_paths` | Y | Relative path of the target directory where selected items will be moved (relative to ZIP home folder) |
| `remove` | N | List of glob patterns of ZIP content to remove after extraction (must include the necessary `target_paths`, they are relative to the section `target_dir`) |
| `execute_after` | N | List of shell commands to execute once ZIP extraction is completed; actions are executed with the section `target_dir` as current working directory |

Nota:
- the `zip_paths` and `target_paths` are matched one-by-one, and must hence have the same length.
- the ZIP is first saved to a temporary location before extraction, consuming some disk space
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

Nota: The `touch` command in `execute_after` is not representative of what you would usually do ^^

```toml
[files.assets.config]
target_dir="src/hatch_openzim/templates/assets"
execute_after=[
    "fix_ogvjs_dist .",
]

[files.assets.actions."jquery.min.js"]
action="get_file"
source="https://code.jquery.com/jquery-3.5.1.min.js"
target_file="jquery.min.js"
execute_after=[
    "touch done.txt",
]

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
