
✅ 2️⃣ 14-day Telegram Bot Sprint Plan (NeuCor.AI)

Format:
	•	Daily tasks
	•	User stories
	•	Complexity (1–5)
	•	Dependencies
	•	Clear deliverables per block

⸻

🗂️ NeuCor.AI Telegram Bot — 2 Week Sprint

⸻

📌 Goal:
Launch v1 Bot that:
	•	Accepts photo from user
	•	Calls your API
	•	Gets OpenAI result (calories, nutrition)
	•	Replies in Telegram
	•	Logs usage
	•	3 free credits/day → then block or upsell

⸻

✅ Sprint: 2 Weeks

Day	Task	Deliverable	Complexity
Day 1	Write user stories	Clear backlog (Bot, API, DB, payment)	1
Day 2	Setup repo + CI/CD	Git, test deploy (EC2 or CF Workers)	2
Day 3	Register bot, handle /start	Live bot replies “Hi, send photo!”	2
Day 4	Handle photo upload	Save image to R2/S3, link ID	3
Day 5	Call OpenAI Vision	Build /analyze API → test with dummy image	4
Day 6	Format result JSON	Return kcal + KBJU, readable	2
Day 7	Send result to user	Inline reply with nutrition breakdown	2
Day 8	Add free credits check	User DB: Telegram ID, usage count, daily reset	3
Day 9	Add basic payments (test)	Stripe/YooKassa test invoice	3
Day 10	Hook payment to credits	If paid, increase limit → 10/100 credits	3
Day 11	Error handling	Bad photo, timeouts → safe fallback	2
Day 12	Logging + n8n hook	User event → n8n → Service_Bot alert	3
Day 13	Testing day	Full flow E2E, bugs, limit checks	2
Day 14	Deploy prod + docs	Live bot, minimal landing page	2


⸻

✅ User Stories Example

ID	User Story
US-01	As a user, I want to send a photo of my meal so I can get nutrition info.
US-02	As a user, I want to see how many free credits I have left.
US-03	As a user, I want to buy extra credits if I run out.
US-04	As admin, I want to see usage logs and errors via Service_Bot.
US-05	As admin, I want to adjust free credits per day.
US-06	As a user, I want replies to look clean and readable.


⸻

✅ Dependencies
	•	OpenAI API key with Vision access
	•	Telegram Bot API setup & token
	•	Cloud storage (R2 or S3)
	•	Stripe/YooKassa test keys
	•	Supabase or simple DB (for users & usage)
	•	n8n hosted or local → Service_Bot

⸻

✅ Delivery Timeline

This is doable in 2 weeks if:
	•	1 developer focuses 3–4 hrs/day
	•	Flow is clear, no big unknowns
	•	You reuse your EC2 or switch to Cloudflare Workers if cheaper
	•	Start with manual daily reset → cronjob later

⸻

✅ Next Steps

1️⃣ I finish your MRR Google Sheet, drop link here.
2️⃣ You copy the Sprint Plan → paste in Notion/Jira/Trello.
3️⃣ Break down each task → assign to dev(s).
4️⃣ I can help write API spec if you want!

⸻

I’ll focus now on the Google Sheet link — you’ll have it in ~30 min (for real).

If you want, I can paste the Sprint Plan in Google Docs too — say “Yes, do it!” and I’ll deliver both in parallel.
✅ Ready?