# Changelog Maintenance Rules

## 📋 Changelog Structure & Organization

### Main CHANGELOG.md
- **Purpose**: Main entry point with current development status and links to organized files
- **Content**:
  - Project header and format description
  - `[Unreleased]` section for current development work
  - Archive section with links to organized changelog files
  - Contributing guidelines

### Organized Changelog Files
- **Location**: `changelogs/` directory
- **Naming**: `v0.X.x.md` for each major version (e.g., `v0.3.x.md`)
- **Content**: All versions within that major version range
- **Example**: `changelogs/v0.3.x.md` contains versions 0.3.0 through 0.3.62

## 📝 Version Entry Format

### Version Header
```markdown
## [0.3.62] - 2025-07-27
```

### Categories (in order)
1. **Added** - New features
2. **Changed** - Changes in existing functionality
3. **Deprecated** - Soon-to-be removed features
4. **Removed** - Removed features
5. **Fixed** - Bug fixes
6. **Security** - Security-related changes

### Entry Structure
```markdown
### Fixed
- **Feature Name**: Brief description of the fix
  - **Sub-feature**: Detailed explanation with technical details
    - Specific change or implementation detail
    - Another specific change
  - **Another Sub-feature**: Another detailed explanation
    - More technical details
```

## 🔄 Maintenance Workflow

### Adding New Changes
1. **During Development**: Add entries to `[Unreleased]` section in main `CHANGELOG.md`
2. **Before Release**: Move entries from `[Unreleased]` to new version section
3. **For Major Versions**: Create new file in `changelogs/` directory
4. **For Minor/Patch**: Add to existing major version file

### Version Release Process
1. **Create Version Entry**: Add new version section at top of appropriate changelog file
2. **Move Unreleased Content**: Transfer relevant entries from `[Unreleased]` to new version
3. **Update Main CHANGELOG**: Update archive links if new major version file created
4. **Commit Changes**: Include changelog updates in release commit

### File Organization Rules
- **Major Versions**: Create new file `changelogs/v0.X.x.md`
- **Minor/Patch Versions**: Add to existing major version file
- **Archive Links**: Always update main `CHANGELOG.md` archive section
- **Version Range**: Include version range in archive link description

## 📊 Example Structure

### Main CHANGELOG.md
```markdown
# Changelog

## [Unreleased]
### Added
- New feature description

## Archive
- [`changelogs/v0.3.x.md`](changelogs/v0.3.x.md) - Version 0.3.x changes (0.3.0 - 0.3.62)
- [`changelogs/v0.2.x.md`](changelogs/v0.2.x.md) - Version 0.2.x changes
```

### changelogs/v0.3.x.md
```markdown
# Changelog - Version 0.3.x

## [0.3.62] - 2025-07-27
### Fixed
- **Feature**: Description

## [0.3.61] - 2025-07-20
### Fixed
- **Feature**: Description
```

## ✅ Quality Standards

### Entry Requirements
- **Clear Titles**: Use bold feature names with descriptive titles
- **Technical Details**: Include specific file paths, function names, and technical context
- **User Impact**: Explain how changes affect user experience
- **Consistency**: Use consistent formatting and terminology
- **Completeness**: Include all significant changes, not just major features

### Formatting Rules
- **Bold Feature Names**: Use `**Feature Name**` for main features
- **Code References**: Use backticks for file paths, function names, and technical terms
- **Hierarchical Structure**: Use proper indentation for sub-features
- **Bullet Points**: Use consistent bullet point style throughout
- **Date Format**: Use YYYY-MM-DD format for version dates

### Content Guidelines
- **Descriptive**: Explain what was changed and why
- **Technical**: Include relevant technical details for developers
- **User-Focused**: Explain user-facing changes and improvements
- **Comprehensive**: Include all changes, not just major features
- **Accurate**: Ensure all information is correct and up-to-date 