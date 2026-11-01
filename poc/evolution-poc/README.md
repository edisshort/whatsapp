# Evolution API POC

Flask dashboard on **port 5002** + [Evolution API](https://github.com/evolution-foundation/evolution-api) on **port 8080**.

## Quick start

1. **Start Evolution** (requires Docker; first run may take a few minutes):
   ```bash
   docker compose up -d
   ```
   Set the same API key in `.env`:
   `EVOLUTION_API_KEY=change-me-evolution-api-key`

2. **Flask app**
   ```bash
   copy .env.example .env
   pip install -r requirements.txt
   python app.py
   ```

3. Open **http://127.0.0.1:5002** → **admin / admin123**

4. **Connect QR** → Create instance → Load QR → scan

5. **Contacts** → Sync · **Compose** → send / campaign

## Mock mode

```env
ENGINE_MOCK=true
```

## Contacts sync

Evolution v2 loads contacts via **POST** `/chat/findContacts/{instance}` with body `{"where": {}}` (GET returns 404).

## Repo

Evolution API: https://github.com/evolution-foundation/evolution-api
