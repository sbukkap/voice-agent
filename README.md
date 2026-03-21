# AI Voice Scheduling Agent

A voice assistant that books, reschedules, and manages calendar appointments through natural conversation.

**Loom Video Recording:** [Insert Link]
**Try it live:** [Insert VAPI Share Link Here]

---

## How it works

The project is split into two parts that talk to each other:

- **VAPI (voice layer):** Handles everything you hear and say — speech-to-text via Deepgram Nova-2, natural language understanding via GPT-4o, and voice activity detection. The agent uses a slot-filling approach to collect what it needs (name, date, time) without interrogating you about each one separately.
- **FastAPI backend:** A Python webhook server running on Render. When the LLM decides to take an action (book, reschedule, cancel), it fires a tool call with structured JSON, and the backend handles the actual Google Calendar operations.

---

## Things I'm actually proud of

**Rescheduling without a database**
There's no separate DB storing appointment state. Instead, the backend queries Google Calendar directly to find existing events, deletes the old one, and writes the new one. Calendar-as-database. It works surprisingly well for an MVP.

**Doesn't annoy you**
If you say "book a meeting for Thursday at 2 PM" in your first message, the agent doesn't ask you for the date and then ask you for the time. It picks up everything you gave it and only asks for what's missing.

**Business hours enforcement**
The agent won't let you book outside Monday–Friday, 9 AM–5 PM. It rejects the request gracefully instead of just silently failing or booking it anyway.

**Mid-sentence changes**
You can change your mind while talking and it handles it. Silence timeouts are tuned so it doesn't cut you off, and the context updates dynamically so a correction mid-sentence doesn't break the JSON schema on the backend.

---

## Stack

- **Language:** Python 3.10+
- **Framework:** FastAPI + Uvicorn
- **APIs:** Google Calendar API, VAPI
- **Deployed on:** Render

---

## Running it locally

```bash
git clone https://github.com/your-username/ai-voice-scheduling-agent.git
cd ai-voice-scheduling-agent
pip install -r requirements.txt
```

You'll need Google OAuth credentials:
- Go to Google Cloud Console and create OAuth 2.0 credentials
- Download and save the file as `credentials.json` in the root directory
- Run the auth flow once to generate `token.json`

Then start the server:

```bash
uvicorn main:app --reload
```

Use `ngrok` or `localtunnel` to expose port 8000, then point your VAPI tool webhooks at the generated URL.

---

## What I'd fix in a v2

- **User identity:** Right now the backend searches calendar events by name, which breaks if two users have the same name. The fix is a Postgres table mapping phone numbers to calendar identifiers.
- **Timezones:** EDT is hardcoded. The right move is passing the client's browser timezone through the VAPI SDK on the frontend so it works globally without any config.