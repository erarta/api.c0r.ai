# 03 – Database Design

Table: `shared_analyses`
| Column | Type | PK? | Notes |
|--------|------|-----|-------|
| token | uuid (text) | ✅ | Deep-link identifier `share_<token>` |
| user_id | uuid |  | Owner reference `users.id` |
| analysis_json | jsonb |  | Full ML service response |
| created_at | timestamptz |  | default now() |
| expires_at | timestamptz |  | now() + interval '30 days' |

Supabase Helper (`common/db/shared_analyses.py`)
```python
async def create_shared_analysis(user_id: str, token: str, analysis: dict) -> None: ...
async def get_shared_analysis(token: str) -> Optional[dict]: ...
async def delete_expired_shared_analyses() -> None: ...
```

Indexes
• PK on token ensures O(1) lookup.
• Optional GIN on `(expires_at)` for cleanup filter.

Retention Policy
• Cron job daily calls `delete_expired_shared_analyses` or configure Supabase RLS + function. 