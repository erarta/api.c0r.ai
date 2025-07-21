# Changelog Organization

This directory contains organized changelog files by version ranges to improve maintainability.

## Structure

- `CURRENT.md` - Current development changes (unreleased)
- `v0.3.x.md` - Version 0.3.x changes (latest stable)
- `v0.2.x.md` - Version 0.2.x changes
- `v0.1.x.md` - Version 0.1.x changes
- `v0.0.x.md` - Version 0.0.x changes (initial development)

## Usage

When adding new changes:
1. Add to `CURRENT.md` during development
2. Move to appropriate version file when releasing
3. Keep only the most recent 50-100 entries in main `CHANGELOG.md`

## Migration Notes

The original `CHANGELOG.md` contained 1040+ lines with many duplicate entries.
This has been cleaned up and organized into version-specific files.