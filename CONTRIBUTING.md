# 📌 Contributing to NeuCor.AI

Thank you for helping build NeuCor.AI!  
This doc explains how to contribute clean, safe code.

---

## ✅ How to Contribute

1️⃣ **Fork the repo**

2️⃣ **Clone your fork**
```bash
git clone https://github.com/YOUR_USERNAME/neneucor.ai.git
cd neneucor.ai

3️⃣ Create a branch

git checkout -b feature/my-new-feature

4️⃣ Write atomic code
	•	One feature per branch.
	•	Follow /modules structure (NeuCor_Bot, Cloudflare_Worker, etc).

5️⃣ Run local tests

6️⃣ Commit with clear messages

git commit -m "feat(bot): add /start command"

7️⃣ Push & create a Pull Request

git push origin feature/my-new-feature

8️⃣ Describe what you did
	•	Add screenshots if needed.
	•	Link related issues.

⸻

✅ Code Guidelines
	•	Use .env for secrets.
	•	Keep linting clean.
	•	Follow TRD modules.
	•	Add clear docstrings/comments.
	•	Test Cloudflare Worker with Wrangler before PR.

⸻

✅ Need help?

Open an Issue or ping the repo owner.

⸻

Let’s build NeuCor.AI together! 🚀