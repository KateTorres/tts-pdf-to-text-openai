# Changelog

All notable changes to this project will be documented in this file, starting 2025-07-03.

## [1.2.0] - 2025-07-03

### Added
- `utils/dialogs.py`: New reusable utility for GUI info dialogs using `tkinter`.
- `utils/paths.py`: New module for reusable path operations (`get_directory`, `get_basename`, `replace_suffix`).
- `utils/logging_utils.py`: Appends structured entries to a JSON log file. Handles missing or malformed files  and ensures logs remain human-readable.
  
### Changed
- Reorganized project structure and replaced most of the previous implementation.
- Migrated to a cleaner codebase with updated logic and improved maintainability.
- Refactored `main.py` to accomodate above changes.

### Notes
- Full feature rewrite from [`feature/refactor-utils`] applied via rebase.
- Original code as of version [1.1.0] preserved under tag `backup-before-rewrite-by-refactor-utils`.
