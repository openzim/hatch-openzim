# hatch-openzim test data

Fixture files used by the `hatch-openzim` test suite (see
`tests/test_files_install.py` and `tests/configs/full.toml`). Tests download
them over HTTP from https://dev.kiwix.org/hatch-openzim/, so they are hosted
there rather than kept only in the git repository.

**Do not delete, rename, or edit these files** without updating the
referencing tests/configs in the `hatch-openzim` repo
(https://github.com/openzim/hatch-openzim) — doing so will break its CI.

## Content

- `file1.txt`: an empty file, used to test the `get_file` action (simply
  downloading a single file).

- `testset1.zip`: used to test the `extract_all` action. Contains:
  - `file1.txt`, `file2.txt`: top-level files
  - `keep1/`: a subfolder with `file1.txt` and `file2.txt`, meant to be kept
  - `remove1/`: a subfolder with `file1.txt` and `file2.txt`, meant to be
    removed by the `remove` config option
  - `remove2.txt`: a top-level file meant to be removed by the `remove`
    config option
  - `remove3/file1.txt`: meant to be removed by the `remove` config option
  - `remove3/file2.txt`: meant to be kept (only its sibling is removed)

- `testset2.zip`: used to test the `extract_items` action. Contains:
  - `keep1/`: a subfolder with `file1.txt`, `file2.txt`, `file1.json` and
    `file2.json`, used to extract either the whole folder or individual
    files/extensions from it
  - `remove2.txt`: a top-level file (unused by current tests, kept for
    parity with `testset1.zip`)
  - `remove3/`: a subfolder with `file1.txt` and `file2.txt` (unused by
    current tests, kept for parity with `testset1.zip`)

All files are intentionally tiny/empty: only their name, path, and
presence/absence matter to the tests, not their content.
