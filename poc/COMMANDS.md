# Command reference — start WAHA & Evolution

Copy-paste commands for Windows (PowerShell or **cmd**). Paths assume repo root: `c:\Users\HP\Downloads\whatsapp`.

**Need:** Docker Desktop running, Python 3.11+.

---

## URLs & logins (cheat sheet)

| Service | URL | Username | Password / key |
|---------|-----|----------|----------------|
| **Flask WAHA app** | http://127.0.0.1:5001 | `admin` | `admin123` |
| **Flask Evolution app** | http://127.0.0.1:5002 | `admin` | `admin123` |
| **WAHA engine API** | http://127.0.0.1:3000 | — | Header `X-Api-Key` (see below) |
| **WAHA Dashboard** | http://127.0.0.1:3000/dashboard/ | See `waha-env\.env` → `WAHA_DASHBOARD_USERNAME` (usually **`admin`**) | `WAHA_DASHBOARD_PASSWORD` in same file |
| **WAHA Swagger** | http://127.0.0.1:3000/ | Same as dashboard | Same as dashboard |
| **Evolution API** | http://127.0.0.1:8080 | — | Header `apikey` (see below) |
| **Evolution Manager** | http://127.0.0.1:8080/manager | *(no username)* | **API Key Global** = `EVOLUTION_API_KEY` (default below) |

### Where secrets live

| Secret | File |
|--------|------|
| WAHA API key + dashboard user/password | `poc\waha-poc\waha-env\.env` (create with `init-waha.bat`) |
| WAHA key for Flask | `poc\waha-poc\.env` → `WAHA_API_KEY` **must match** `waha-env\.env` |
| Evolution API key | `poc\evolution-poc\docker-compose.yml` → `AUTHENTICATION_API_KEY` |
| Evolution key for Flask | `poc\evolution-poc\.env` → `EVOLUTION_API_KEY` **must match** compose |

Default Evolution key in this repo (change in production):

```text
change-me-evolution-api-key
```

WAHA dashboard worker: after login, set server URL `http://127.0.0.1:3000` and paste **`WAHA_API_KEY`** from `waha-env\.env`.

---

## One-time setup

### WAHA credentials

```bat
cd c:\Users\HP\Downloads\whatsapp\poc\waha-poc
init-waha.bat
```

Copy `WAHA_API_KEY` from `waha-env\.env` into `poc\waha-poc\.env`.

### Flask `.env` files (if missing)

```bat
cd c:\Users\HP\Downloads\whatsapp\poc\waha-poc
copy .env.example .env

cd c:\Users\HP\Downloads\whatsapp\poc\evolution-poc
copy .env.example .env
```

```bat
pip install -r requirements.txt
```

Run `pip install` inside **each** POC folder (`waha-poc` and `evolution-poc`).

---

## Start both engines (Docker)

**Terminal 1 — WAHA**

```bat
cd c:\Users\HP\Downloads\whatsapp\poc\waha-poc
docker compose up -d
```

**Terminal 2 — Evolution**

```bat
cd c:\Users\HP\Downloads\whatsapp\poc\evolution-poc
docker compose up -d
```

Check:

```powershell
docker compose -f c:\Users\HP\Downloads\whatsapp\poc\waha-poc\docker-compose.yml ps
docker compose -f c:\Users\HP\Downloads\whatsapp\poc\evolution-poc\docker-compose.yml ps
```

---

## Start both Flask apps

**Terminal 3 — WAHA UI (port 5001)**

```bat
cd c:\Users\HP\Downloads\whatsapp\poc\waha-poc
python app.py
```

**Terminal 4 — Evolution UI (port 5002)**

```bat
cd c:\Users\HP\Downloads\whatsapp\poc\evolution-poc
python app.py
```

Or use batch files if present:

```bat
cd c:\Users\HP\Downloads\whatsapp\poc\waha-poc
start.bat

cd c:\Users\HP\Downloads\whatsapp\poc\evolution-poc
start.bat
```

---

## Health checks (optional)

**WAHA** (replace `YOUR_WAHA_API_KEY`):

```powershell
curl.exe -H "X-Api-Key: YOUR_WAHA_API_KEY" http://127.0.0.1:3000/api/sessions
```

**Evolution**:

```powershell
curl.exe -H "apikey: change-me-evolution-api-key" http://127.0.0.1:8080/
```

---

## Stop everything

In each POC folder:

```bat
docker compose down
```

Stop each `python app.py` with **Ctrl+C**.

---

## Port map (same machine)

| Port | Service |
|------|---------|
| 3000 | WAHA API + dashboard |
| 8080 | Evolution API + manager |
| 5001 | Flask WAHA demo |
| 5002 | Flask Evolution demo |

---

## Full guide

Step-by-step troubleshooting: [GETTING_STARTED.md](./GETTING_STARTED.md)
