# ScanFlow 🧾🤖

**Version:** 0.1 (MVP)

A Telegram bot for automated personal expense tracking powered by AI.
Users simply send a photo of a receipt, and the system recognizes items, categorizes them, and saves everything into a structured database.

## 🛠 Tech Stack
- **Frontend:** Telegram Bot (Python, aiogram 3)
- **Backend:** n8n (Self-hosted workflow automation)
- **AI Engine:** Google Gemini 1.5 Flash (OCR & Data Extraction)
- **Database:** PostgreSQL (via Supabase)
- **Infrastructure:** Docker & Docker Compose (VPS)

## 🚀 Features (v0.1)
- [x] **Image Processing:** Accepts receipt photos via Telegram.
- [x] **AI Parsing:** Extracts date, merchant, currency, and line items using LLM.
- [x] **Smart Categorization:** Automatically assigns categories (e.g., Food, Transport) from a predefined list.
- [x] **Relational DB:** Stores data in a normalized PostgreSQL schema (Users -> Receipts -> Items).
- [x] **User Feedback:** Asynchronous notifications upon successful data entry.

## 📦 Deployment
1. Clone the repository.
2. Create `.env` file with required tokens.
3. Run `docker compose up -d`.
4. Import `n8n_workflow.json` into n8n.