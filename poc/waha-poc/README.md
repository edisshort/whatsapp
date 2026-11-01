# WAHA POC

Flask dashboard on **port 5001** + [WAHA](https://github.com/devlikeapro/waha) on **port 3000**.

## Quick start

### 1. Generate WAHA credentials (required)

Recent WAHA versions reject the old placeholder `0000…` key. Run once:

```bat
init-waha.bat
```

This creates `waha-env/.env` with `WAHA_API_KEY=...`

Copy that key into **Flask** `.env`:

```env
WAHA_API_KEY=<same value as waha-env/.env>
```

### 2. Start WAHA

```bash
docker compose up -d
```

### 3. Start Flask

```bash
copy .env.example .env
pip install -r requirements.txt
python app.py
```

Open **http://127.0.0.1:5001** — login **admin / admin123**

### 4. Connect

**Connect QR** → **Start session** → **Load QR** → scan on phone → **Contacts** → Sync → **Compose**

## Troubleshooting 401 Unauthorized

- `WAHA_API_KEY` in Flask `.env` must **exactly match** `waha-env/.env`
- After changing keys: `docker compose down && docker compose up -d`
- Test: `curl.exe -H "X-Api-Key: YOUR_KEY" http://127.0.0.1:3000/api/sessions`

## Mock mode (no Docker)

```env
ENGINE_MOCK=true
```
