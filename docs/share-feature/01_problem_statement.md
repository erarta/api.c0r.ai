# 01 – Problem Statement

Users receive a rich nutrition analysis of their meal in a private chat with the bot. They frequently ask to *share* this analysis with friends or group chats.

Requirements
1. One-tap experience – no copy-paste.
2. Preserve full Markdown formatting, emojis & language.
3. Keep original user anonymous (privacy).
4. Work in private chats & groups.
5. Minimal new infrastructure; reuse existing Supabase & bot codebase.
6. Tokens must expire (30 days) or be revocable.
7. Feature must be covered by unit & integration tests.

Out-of-scope: building Web-Apps, generating images/PDFs, inline-mode keyboards. 