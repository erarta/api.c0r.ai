# 08 – Tests Plan

| Level | Scenario | Expected |
|-------|----------|----------|
| Unit | `create_shared_analysis` inserts row | Row exists |
| Unit | `get_shared_analysis` returns None for invalid token | None |
| Unit | Expired token check | Exception message |
| Handler | `/start share_<token>` valid | Sends analysis text |
| Handler | `/start share_invalid` | Sends invalid msg |
| Integration | Full happy path (photo → analysis → share → second user) | Works |

Mocks
• Supabase client mocked with `pytest-asyncio` fixtures.
• Aiogram `Bot` & `Message` objects mocked via `aiogram.tests` utilities.

Coverage target ≥ 90 % for new code. 