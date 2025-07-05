Excellent practical follow-up questions — let’s tackle them precisely, line by line 👇

⸻

📷 1️⃣ Average photo size iPhone 16 Pro

For food photos taken with a modern iPhone:
	•	Typical 12–48 megapixel photo = 2 MB to 6 MB.
	•	If it’s HEIC format, smaller: 1–3 MB.
	•	If user sends a screenshot → smaller.
	•	If user uses “send compressed” in Telegram → often ~500 KB – 1 MB.

Edge function limit:
Cloudflare Workers have a 10 MB request limit.
So one raw iPhone photo is fine, but if people send 2–3 at once → too big.

✅ Good practice: Ask user to send one plate only per photo + compress server-side if needed.

⸻

☁️ 2️⃣ Why not use Cloudflare R2?

Great idea — you absolutely can!
	•	R2 = Cloudflare’s S3 alternative, globally distributed, no egress fees if you keep it in their edge.
	•	Free 10 GB storage → enough for thousands of photos if you delete them frequently.
	•	Fast → sits near your Worker → very low latency.
	•	Built-in easy signed URL for privacy.
	•	Better than Supabase Storage if you want tight integration with Cloudflare.

✅ So yes: R2 is perfect for your use case.

Your flow:

Bot → uploads photo → Worker → save to R2 → pass signed URL to inference → delete after X days


⸻

💳 3️⃣ Payments in Russia

Good point — Stripe doesn’t support Russia directly (as of 2025).

Options:
	•	💡 Use Yookassa (Yandex.Kassa) — popular for Russian payments, supports cards, SBP, wallets.
	•	💡 Or Robokassa, CloudPayments, Tinkoff Pay — all work well.
	•	💡 For global — still keep Stripe for EU/US users later.
	•	💡 If you have legal entity abroad (LLC in UAE, KZ, Armenia), you can still run Stripe on that.

So:
	•	For Russia: Yookassa → easiest.
	•	For international: Stripe → perfect.

✅ How to merge: Both go through your own landing page cor.diet/pay. After payment → same webhook → Supabase is_premium = true.

⸻

🎯 4️⃣ 5 free / day — too much?

Spot on — let’s do the math:
	•	A typical user eats 3 meals / day → so if you give 3 free they can fully test it daily.
	•	If you want faster upgrade → do 1 free per day, then lock. Or 3 free total for lifetime, then upgrade.
	•	Many freemium bots do low free usage to push upgrade.

✅ My suggestion:
	•	Start with 3 free TOTAL → lifetime → not daily.
	•	Add “Invite a friend to get +1 free scan” for virality.
	•	Offer daily free if you want to push retention later.

⸻

💸 5️⃣ How much does 1 scan cost you?

Rough estimate if using GPT-4 Vision:
	•	GPT-4 Vision: ~0.01$ to 0.03$ per image depending on size + prompt.
	•	If you use OpenAI + 3rd-party detection, maybe $0.05 max per photo.
	•	If you use your own model later → cost near zero (just GPU cost).

✅ So:
	•	3 free photos = $0.15 per user max.
	•	If 1000 free users → $150 in compute.
	•	Very manageable if you control free usage.

⸻

📌 ✅ Key call here

Decision	Recommendation
Photo storage	Cloudflare R2 — yes, perfect
Payments RU	Yookassa for Russia, Stripe for ROW
Free usage	3 free total per user at launch
API cost	$0.03–$0.05 max per photo with GPT-4 Vision


⸻

🟢 If you want, I can prep
	•	How to connect R2 + Cloudflare Worker with signed URLs.
	•	Simple Yookassa payment flow with webhooks.
	•	Example cost projection table for 1k / 10k users.

Just say “Show me the next step” — and I’ll prepare the practical starter pack 🚀