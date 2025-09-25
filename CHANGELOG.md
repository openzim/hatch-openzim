# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.3] - 2025-09-25

### Fixed

-  Widen dependencies ranges since this is used by many projects #22

## [0.2.2] - 2025-01-20

### Changed

- Add support for Python 3.13, remove support for Python 3.8 (#19)

## [0.2.1] - 2024-05-06

### Fixed

- Indentation of `execute_after` logs is too deep  #15

### Changed

- `execute_after` does not display detailled logs of stuff run #16

## [0.2.0] - 2024-02-16

### Added

- Metadata hook: add suport for additional-classifiers property #10

### Fixed

- Build hook: fix issue with extract_items when target_path is in a subfolder #11
- Tests: ensure tests are also ok when ran from a fork or outside any Git structure #13

## [0.1.0] - 2024-02-05

### Added

- Initial release
