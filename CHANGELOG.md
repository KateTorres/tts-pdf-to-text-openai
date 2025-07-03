All notable changes to this project will be documented in this file starting 2025-07-03.

## [1.2.0] - 2025-07-03
### Changed
- Reorganized project structure and replaced most of the previous implementation.
- Migrated to a cleaner codebase with updated logic and improved maintainability.
- Full feature rewrite: [(feature/refactor-utils] applied via rebase.
- Original code [1.1.0] was preserved under tag `backup-before-rewrite-by-refactor-utils`.
- Refactored main.py 

### Added
- `utils/dialogs.py`: New reusable utility for GUI info dialogs using `tkinter`.
- `utils/paths.py`: New module for reusable path operations (`get_directory`, `get_basename`, `replace_suffix`).
- `utils/file_handler.py`: Moved last directory tracking logic into reusable module with `get_last_directory()` and `save_last_directory()` functions.
