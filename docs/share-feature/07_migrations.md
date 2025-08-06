# 07 – Migrations

### Supabase SQL Migration (`migrations/database/2025-08-10_add_shared_analyses.sql`)
```sql
create table if not exists shared_analyses (
  token uuid primary key,
  user_id uuid references users(id) on delete cascade,
  analysis_json jsonb not null,
  created_at timestamptz default now(),
  expires_at timestamptz default (now() + interval '30 days')
);
create index if not exists idx_shared_analyses_expires_at on shared_analyses(expires_at);
```

### Python helper script
If offline migration tool is used (Alembic), generate matching revision.

### Cleanup Job
```sql
delete from shared_analyses where expires_at < now();
```
Schedule with Supabase Edge Function or cron in `scripts/`. 