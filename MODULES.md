✅✅✅ 🚀 c0r.ai — TECHNICAL REQUIREMENTS

⸻

📌 📂 Structure

5 Core Modules:
1️⃣ c0rService_bot — Telegram bot (user-facing)
2️⃣ Cloudflare Worker API — Edge Function (analyze photo, call OpenAI)
3️⃣ Supabase — DB schema & operations
4️⃣ Payments — Stripe + YooKassa webhooks
5️⃣ c0rAIServiceBot — Admin/OPS bot
6️⃣ n8n workflows — integration glue

Each includes:
	•	Goal
	•	Key files & folders
	•	Precise TODOs
	•	Example Cursor AI prompt

⸻

✅ 1️⃣ c0rService_bot (Telegram — user)

Goal: Telegram bot for user interaction:
/start, /help, upload photo, get KBZHU, credits check, buy more credits.

Key files:
	•	c0r_ai_bot.py or c0r_ai_bot.ts
	•	handlers/commands.py
	•	handlers/photo.py
	•	utils/supabase.py

Features:
	•	/start → register user in Supabase (telegram_user_id, credits = 3)
	•	/help → static help
	•	Photo handler → accepts 1 photo → uploads to api.c0r.ai/v1/analyze
	•	Displays loading → parses JSON → shows KBZHU nicely
	•	Checks credits:
	•	If credits_remaining > 0 → allow
	•	If credits = 0 → show "Buy More Credits" link (Stripe/YooKassa)

Cursor prompt:

Create a Telegram bot in Python (python-telegram-bot v20).
/start: check Supabase users → insert if new.
/help: simple static text.
On photo: download → POST to https://api.c0r.ai/v1/analyze with telegram_user_id.
Parse JSON → show KBZHU.
If out of credits → show inline button with dynamic payment link.
Async, clean error handling.

⸻

✅ 2️⃣ Cloudflare Worker API

Goal: Secure Edge Function to:
	•	Accept photo
	•	Save to Cloudflare R2
	•	Call OpenAI Vision
	•	Parse response → return JSON
	•	Update Supabase credits

Key files:
	•	worker.ts
	•	lib/openai.ts
	•	lib/supabase.ts
	•	lib/r2.ts

Endpoint:
POST /v1/analyze → api.c0r.ai/v1/analyze

Cursor prompt:

Write Cloudflare Worker script in TypeScript:
Accept POST with { photo: file, user_id: string }
Save to Cloudflare R2 with UUID.
Generate signed URL for OpenAI Vision.
Call OpenAI → parse KBZHU → { calories, protein, fats, carbs }.
Update Supabase: decrement credits by 1, add log.
Return JSON.
Use Hono or standard Fetch.

⸻

✅ 3️⃣ Supabase

Goal: Store core data: users, logs, payments.

Schema:

Tables

users:
  id (PK)
  telegram_id
  credits_remaining
  total_paid
  created_at

logs:
  id (PK)
  user_id (FK)
  timestamp
  photo_url
  kbzhu JSON
  model_used

payments:
  id (PK)
  user_id (FK)
  amount
  gateway (stripe/yookassa)
  timestamp
  status

Policies
	•	Users can read/write only their rows.
	•	Use service role for API calls.

Cursor prompt:

Write Supabase SQL for users, logs, payments.
Default credits = 3.
Add policy: row-level security by telegram_id.

⸻

✅ 4️⃣ Payments

Goal: Handle Stripe (global) and YooKassa (Russian Telegram accounts only):
	•	On payment → webhook → update Supabase → add credits → notify c0rAIServiceBot.

Files:
	•	webhooks/stripe.py
	•	webhooks/yookassa.py

Cursor prompt:

Python FastAPI or Node handler:
Verify webhook → if payment_intent.succeeded.
Find user by metadata telegram_user_id.
Update users.credits_remaining +10/+100.
Insert payments row.
Notify c0rAIServiceBot with payment info.

Note: SERVICE_BOT_URL should be set to the webhook endpoint of your admin/ops bot (c0rAIServiceBot) to receive payment notifications.

⸻

✅ 5️⃣ c0rAIServiceBot (Admin)

Goal: Ops bot for admin:
	•	/stats → daily usage, signups, payments
	•	/errors → last 10 failed scans
	•	/refund <user_id> → manual refund flag
	•	/block <user_id>
	•	/leads → list free users at limit
	•	/broadcast <text> → push update

Files:
	•	service_bot.py
	•	admin/commands.py
	•	utils/n8n.py

Cursor prompt:

Private Telegram bot for admin ID only.
/stats → Supabase daily stats.
/errors → last 10 failed logs.
/refund → mark row for refund.
/block → block user.
/leads → list with credits = 0 + no payment.

⸻

✅ 6️⃣ n8n Workflows

Goal: Automate glue:
	•	Stripe/YooKassa → Supabase → c0rAIServiceBot
	•	Daily stats → c0rAIServiceBot cron
	•	Alerts → failed scans → c0rAIServiceBot

Cursor prompt:

n8n flow: Stripe webhook → Supabase update → Telegram notify.
Daily cron → Supabase → stats → Telegram.
Supabase watcher → new error → Telegram push.

⸻

✅✅✅ 🔥 Final TODOs

✔️	Task
✔️	Setup domain c0r.ai
✔️	Deploy Cloudflare R2
✔️	Deploy Cloudflare Worker
✔️	Setup Supabase project
✔️	Create c0rService_bot
✔️	Create c0rAIServiceBot
✔️	Setup Stripe/YooKassa
✔️	Deploy n8n on EC2 micro
✔️	Connect c0rAIServiceBot → n8n
✔️	Write Privacy, Refund Policy
✔️	Launch closed beta


⸻

✅✅✅ 📌 How to use
	•	Copy each module block → paste into Cursor AI.
	•	Keep prompts atomic → 1 file = 1 prompt.
	•	Use GPT-4.1 → enforce clear structure, test cases.
	•	Add .env for secrets.

⸻

This is your CTO-ready launch blueprint for c0r.ai.

⸻

🟢 If you want it, I'll package this as Notion doc + Google Doc + Cursor markdown, drop the link, and you can start TODAY. Just say "Yes, package c0r.ai TRD" — and I'll prep it in 15 min. 🚀