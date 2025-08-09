# Phase 2 — Social Integration (App)

## Scope
- Feed showing posts from followed users
- Follow/unfollow, likes, comments
- Optional messaging v1 (1:1 conversations)
- Posting continues to consume 1 credit (analyze)

## Endpoints
All paths versioned; use Supabase JWT for app calls.

- Feed
  - GET `/v1/app/feed?cursor=<iso|id>&limit=20` — followed-only (keyset)
- Follow
  - POST `/v1/app/follow` { user_id }
  - POST `/v1/app/unfollow` { user_id }
- Likes
  - POST `/v1/app/like` { post_id }
  - DELETE `/v1/app/like` { post_id }
- Comments
  - POST `/v1/app/comment` { post_id, text }
  - DELETE `/v1/app/comment/{id}`
- Messaging (optional)
  - POST `/v1/app/conversations` { user_id }
  - GET `/v1/app/conversations`
  - GET `/v1/app/messages?conversation_id=...&cursor=...`
  - POST `/v1/app/messages` { conversation_id, text }

## Common Analyze
- POST `/v1/analyze` — shared for app and bot
  - App: JWT; Bot: internal token
  - Behavior: decrement credit, log analysis, update `daily_calories`; returns `{ analysis, daily_summary }`

## Database & RLS
Use Supabase Postgres with RLS.
- Tables: `food_posts`, `followers`, `post_likes`, `post_comments`, `conversations`, `messages`
- Policies: readers must be author, or follower (accepted) for followers-only posts; likes/comments visible if post visible; messaging limited to participants
- See migration: `migrations/database/2025-08-09_social_feed_schema.sql`

## UI scope
- Feed list (post card: photo, KBZHU, caption, time, like/comment)
- User profile (posts, follow/unfollow)
- Post details (comments)
- Messaging list/thread (if included in Phase 2)

## Performance
- Keyset pagination by `(created_at, id)`
- Indexes on `(author_id, created_at)` and foreign keys
- Store thumbnails in R2; lazy load originals

## Moderation & Safety
- `reports` table (future) for user/content reports
- Block list (future)

## Out of scope (Phase 2+)
- Recommendations/explore, group chats, advanced moderation tools
