# Claude Code Project Rules

## Database Migrations
- **ALWAYS** test locally first: `env ENVIRONMENT=development DB_PASSWORD='&vh1NzI6wwiUx' ./scripts/run_migrations.sh`
- **ALWAYS** create both migration and rollback files
- Use templates from `docs/CLAUDE_MIGRATIONS_CHEATSHEET.md`
- Never modify existing migration files after applied
- Push to main automatically deploys via GitHub Actions

## Testing & Deployment
- Run tests before deployment: `npm test` or equivalent
- Check production after deployment
- Never commit sensitive data

## Project Structure
- Migrations: `migrations/database/` and `migrations/rollbacks/`
- Documentation: `docs/`
- Scripts: `scripts/`

## Quick Commands
```bash
# Test migration locally
env ENVIRONMENT=development DB_PASSWORD='&vh1NzI6wwiUx' ./scripts/run_migrations.sh

# Standard commit
git add . && git commit -m "feat: description" && git push origin main
```