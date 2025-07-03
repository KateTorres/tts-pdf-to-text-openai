# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- `utils/dialogs.py`: New reusable utility for GUI info dialogs using `tkinter`.
- `utils/paths.py`: New module for reusable path operations (`get_directory`, `get_basename`, `replace_suffix`).
- `utils/file_handler.py`: Moved last directory tracking logic into reusable module with `get_last_directory()` and `save_last_directory()` functions.
- `requirements.txt`: Confirmed inclusion of `chardet`; `tkinter` usage clarified via README comments.
- `run_unwrapper.sh` and `run_unwrapper.bat`: Shell and batch launchers for cross-platform execution.

### Changed
- `main.py`: Refactored to use `dialogs.show_info()`, `paths.get_directory()`, and `file_handler` instead of inline logic.
- `text_loader.py`: Keeps `log_encoding()` in the loader to preserve encapsulation (per SRP).

### Fixed
- Git line ending warning: recommended `.gitattributes` or `core.autocrlf` guidance for `.sh` files on Windows.
