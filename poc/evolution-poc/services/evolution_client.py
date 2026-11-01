import logging
from typing import Any

import requests

from config import Config

log = logging.getLogger(__name__)


class EvolutionError(Exception):
    pass


class EvolutionClient:
    def __init__(self):
        self.base = Config.EVOLUTION_BASE_URL
        self.instance = Config.EVOLUTION_INSTANCE
        self.mock = Config.ENGINE_MOCK

    def _headers(self) -> dict:
        return {"apikey": Config.EVOLUTION_API_KEY, "Content-Type": "application/json"}

    def _request(self, method: str, path: str, **kwargs) -> Any:
        if self.mock:
            return self._mock(method, path, **kwargs)
        url = f"{self.base}{path}"
        try:
            resp = requests.request(method, url, headers=self._headers(), timeout=120, **kwargs)
        except requests.RequestException as exc:
            raise EvolutionError(f"Evolution unreachable at {self.base}: {exc}") from exc
        if resp.status_code >= 400:
            raise EvolutionError(f"Evolution {resp.status_code}: {resp.text[:500]}")
        if resp.content and "application/json" in resp.headers.get("content-type", ""):
            return resp.json()
        return resp.text

    def health(self) -> dict:
        try:
            self._request("GET", "/")
            return {"ok": True}
        except EvolutionError as e:
            return {"ok": False, "error": str(e)}

    def create_instance(self) -> dict:
        body = {
            "instanceName": self.instance,
            "qrcode": True,
            "integration": "WHATSAPP-BAILEYS",
        }
        return self._request("POST", "/instance/create", json=body)

    def connect(self) -> dict:
        return self._request("GET", f"/instance/connect/{self.instance}")

    def connection_state(self) -> dict:
        return self._request("GET", f"/instance/connectionState/{self.instance}")

    def get_session(self) -> dict:
        state = self.connection_state()
        inner = state.get("instance", state)
        status = inner.get("state") or inner.get("status") or "unknown"
        return {"name": self.instance, "status": status, "raw": state}

    def get_qr_payload(self) -> dict:
        data = self.connect()
        return data

    def fetch_contacts(self) -> list[dict]:
        # Evolution v2: POST with filter body (GET returns 404)
        data = self._request(
            "POST",
            f"/chat/findContacts/{self.instance}",
            json={"where": {}},
        )
        if isinstance(data, list):
            return data
        inner = data.get("response") if isinstance(data, dict) else None
        if isinstance(inner, list):
            return inner
        return data.get("contacts", []) if isinstance(data, dict) else []

    def send_text(self, phone_digits: str, text: str) -> dict:
        number = phone_digits.lstrip("+").replace("@c.us", "")
        return self._request(
            "POST",
            f"/message/sendText/{self.instance}",
            json={"number": number, "text": text},
        )

    def logout_instance(self) -> dict:
        return self._request("DELETE", f"/instance/logout/{self.instance}")

    def _mock(self, method: str, path: str, **kwargs) -> Any:
        if "connectionState" in path:
            return {"instance": {"state": "open", "status": "WORKING"}}
        if "connect" in path:
            return {"base64": "", "code": "mock-qr", "pairingCode": None}
        if "findContacts" in path:
            return [
                {"id": "919876543210@s.whatsapp.net", "pushName": "Demo A"},
                {"id": "919876543211@s.whatsapp.net", "pushName": "Demo B"},
            ]
        if "sendText" in path:
            return {"mock": True, "sent": True}
        if path == "/instance/create":
            return {"instance": {"instanceName": self.instance}}
        if path == "/":
            return {"status": "ok"}
        if "logout" in path:
            return {"status": "logged_out"}
        return {}
