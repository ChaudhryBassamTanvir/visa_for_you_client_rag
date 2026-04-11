venv\Scripts\activate
uvicorn main:app --reload
pip install langchain-google-genai python-dotenv
python register_trello_webhook.py
python test_trello_card.py
pip install resend
ngrok http 8000

winget install --id Cloudflare.cloudflared


https://calculator-namely-expected-josh.trycloudflare.com // It will change every time 
Go to https://developers.facebook.com/apps → Your App → WhatsApp → Configuration
Click "Edit" under Webhook
Update Callback URL to:

# AI Client Agent - Run Guide

## Every Time You Start the Project

### Terminal 1 — Cloudflare Tunnel (Public URL)
```bash
cloudflared tunnel --url http://localhost:8000
```


ngrok http 8000 --url exanthematic-reynalda-untamely.ngrok-free.dev

Copy the `https://xxxx.trycloudflare.com` URL
Update it in Meta Dashboard → WhatsApp → Configuration → Webhook → Edit

### Terminal 2 — Backend (FastAPI)
```bash
cd D:\software\CMIT Internship\WebDevelopment\ai-client-updated\backend
venv\Scripts\activate
uvicorn main:app --reload
```

### Terminal 3 — Slack Bot
```bash
cd D:\software\CMIT Internship\WebDevelopment\ai-client-updated\backend
venv\Scripts\activate
python run_slack.py
```

### Terminal 4 — Frontend
```bash
cd D:\software\CMIT Internship\WebDevelopment\ai-client-updated\frontend
npm run dev
```

---

## ⚠️ Important Notes

- **Cloudflare URL changes every restart** → always update it in Meta Dashboard
- **WhatsApp Webhook URL**: `https://xxxx.trycloudflare.com/whatsapp/webhook`
- **Verify Token**: `mysecretverify123`
- All 4 terminals must be running at the same time

---

## Meta Webhook Update Steps (every restart)
1. Go to https://developers.facebook.com/apps
2. Your App → WhatsApp → Configuration
3. Edit Webhook → paste new Cloudflare URL
4. Click Verify and Save




pip install psycopg2-binary sqlalchemy