# Changelog Maintenance Rules

## Core Principle
Every code change MUST update the appropriate changelog file. Changes are organized by version ranges in separate files for better maintainability.

## Changelog Structure
```
changelogs/
├── README.md              # Organization and usage guide
├── CURRENT.md            # Current development changes (unreleased)
├── v0.3.x.md            # Version 0.3.x changes (latest stable)
├── v0.2.x.md            # Version 0.2.x changes
├── v0.1.x.md            # Version 0.1.x changes
└── v0.0.x.md            # Version 0.0.x changes (initial development)
```

## Update Requirements

### During Development
- Add all changes to `changelogs/CURRENT.md`
- Use semantic versioning format: `## [Unreleased]`
- Group changes by type: Added, Changed, Fixed, Removed, Security

### During Release
- Move changes from `CURRENT.md` to appropriate version file
- Update version number: `## [0.3.62] - 2025-01-26`
- Keep main `CHANGELOG.md` with only recent 50-100 entries
- Archive older entries in version-specific files

## Entry Format
```markdown
## [Version] - YYYY-MM-DD

### Added
- **Feature Name**: Description of what was added

### Changed
- **Component**: Description of what was changed

### Fixed
- **Bug Description**: Description of what was fixed

### Removed
- **Feature**: Description of what was removed

### Security
- **Security Issue**: Description of security improvement
```

## Content Standards
- Use clear, descriptive titles with component names
- Include context about why the change was made
- Reference related issues or PRs when applicable
- Use consistent formatting and emoji indicators
- Write from user perspective, not technical implementation

## File Management
- Keep version files under 200 entries each
- Create new version file when current exceeds limit
- Maintain chronological order (newest first)
- Update `changelogs/README.md` when adding new version files

## Checklist
Before each commit:
- [ ] Changes documented in appropriate changelog file
- [ ] Entry follows standard format
- [ ] Description is clear and user-focused
- [ ] Version and date are correct
- [ ] Related changes are grouped together

## Integration with Rules
This rule works together with:
- Documentation maintenance (update docs when features change)
- Migration maintenance (document database changes)
- Testing maintenance (document test coverage changes)
- i18n maintenance (document translation updates)

## Automation
```bash
# Validate changelog format
markdownlint changelogs/*.md

# Check for unreleased changes
grep -r "Unreleased" changelogs/

# Generate release notes
python scripts/generate_release_notes.py
```

Changelog maintenance ensures clear communication of project evolution to users and developers.