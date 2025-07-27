/neneucor.ai
 ├── README.md
 ├── CONTRIBUTING.md
 ├── LICENSE
 ├── .env.example
 ├── /NeuCor_Bot
 │   ├── neucor_bot.py
 │   ├── handlers/commands.py
 │   ├── handlers/photo.py
 │   ├── utils/supabase.py
 ├── /Cloudflare_Worker
 │   ├── worker.ts
 │   ├── lib/openai.ts
 │   ├── lib/supabase.ts
 │   ├── lib/r2.ts
 ├── /Payments
 │   ├── stripe_webhook.py
 │   ├── yookassa_webhook.py
 ├── /NeuCor_Service_Bot
 │   ├── service_bot.py
 │   ├── admin/commands.py
 │   ├── utils/n8n.py
 ├── /n8n_Workflows
 │   ├── README.md
 │   ├── docs/flows.md