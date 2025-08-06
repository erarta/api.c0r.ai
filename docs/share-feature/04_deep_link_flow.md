# 04 – Deep-Link Flow

```mermaid
sequenceDiagram
participant U as User A (owner)
participant B as Bot
participant DB as Supabase
participant V as User B (viewer)
participant S as Social Apps

U->>B: receives analysis
B->>DB: INSERT shared_analyses(token, data)
B-->>U: Analysis message + 2 share buttons
U->>V: forwards link `https://t.me/Bot?start=share_<t>`
V->>B: /start share_<t>
B->>DB: SELECT * FROM shared_analyses WHERE token=<t>
DB-->>B: analysis_json
B-->>V: Formatted analysis message (no share button)

Note over U,S: Alternative: Native Sharing
U->>B: clicks "Share to Social"
B-->>U: inline query result
U->>S: native share sheet opens
S-->>U: user selects app (WhatsApp, Instagram, etc.)
```

## Two Sharing Options

### 1. Deep-link (Telegram-to-Telegram)
- Works within Telegram ecosystem
- Preserves full formatting and emojis
- Requires bot to be available to viewer

### 2. Native Sharing (Cross-platform)
- Uses device's native share sheet
- Works with any installed social app
- Text-only sharing with hashtags
- Better for social media discovery

Edge Cases
1. **Expired token** – bot replies with "Link expired".
2. **Token not found** – "Invalid share link".
3. **Token reused** – allowed; multiple viewers OK.
4. **Owner deletes account** – data auto-purged by foreign-key cascade.
5. **Inline mode disabled** – native share button hidden or shows error.

Note: Share buttons only appear in the original analysis message, not in shared copies. 