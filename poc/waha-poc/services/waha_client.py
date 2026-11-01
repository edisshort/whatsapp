import logging
import time
from typing import Any

import requests

from config import Config

log = logging.getLogger(__name__)

CONNECTED_STATUSES = frozenset({"WORKING", "OPEN", "CONNECTED", "AUTHENTICATED", "READY"})
QR_READY_STATUSES = frozenset({"SCAN_QR_CODE", "SCAN_QR", "QRCODE", "QRCODE_SCAN"})
WAIT_STATUSES = frozenset({"STARTING", "STARTING_SESSION"})


def normalize_status(info: dict) -> str:
    if not info:
        return "UNKNOWN"
    raw = info.get("status") or info.get("state") or "UNKNOWN"
    if isinstance(raw, dict):
        raw = raw.get("status") or raw.get("state") or "UNKNOWN"
    return str(raw).upper().replace(" ", "_").replace("-", "_")


class WahaError(Exception):
    pass


class WahaClient:
    def __init__(self):
        self.base = Config.WAHA_BASE_URL
        self.session_name = Config.WAHA_SESSION
        self.mock = Config.ENGINE_MOCK

    def _headers(self, json_accept: bool = True) -> dict:
        h = {}
        if Config.WAHA_API_KEY:
            h["X-Api-Key"] = Config.WAHA_API_KEY
        if json_accept:
            h["Accept"] = "application/json"
        return h

    def _request(self, method: str, path: str, **kwargs) -> Any:
        if self.mock:
            return self._mock(method, path, **kwargs)
        url = f"{self.base}{path}"
        try:
            resp = requests.request(method, url, headers=self._headers(), timeout=60, **kwargs)
        except requests.RequestException as exc:
            raise WahaError(f"WAHA unreachable at {self.base}: {exc}") from exc
        if resp.status_code >= 400:
            raise WahaError(f"WAHA {resp.status_code}: {resp.text[:400]}")
        if resp.content and resp.headers.get("content-type", "").startswith("application/json"):
            return resp.json()
        return resp.content

    def health(self) -> dict:
        try:
            data = self._request("GET", "/api/sessions")
            return {"ok": True, "sessions": data}
        except WahaError as e:
            return {"ok": False, "error": str(e)}

    def ensure_session(self) -> dict:
        sessions = self._request("GET", "/api/sessions")
        names = {s.get("name") for s in (sessions if isinstance(sessions, list) else [])}
        if self.session_name not in names:
            self._request(
                "POST",
                "/api/sessions",
                json={"name": self.session_name, "config": {}},
            )
        return self.get_session()

    def start_session(self) -> dict:
        self.ensure_session()
        return self._request("POST", f"/api/sessions/{self.session_name}/start", json={})

    def get_session(self) -> dict:
        data = self._request("GET", f"/api/sessions/{self.session_name}")
        if isinstance(data, dict):
            data["_normalized_status"] = normalize_status(data)
        return data

    def wait_for_status(
        self,
        targets: frozenset[str],
        timeout_sec: float = 45,
        interval_sec: float = 1.5,
    ) -> str:
        deadline = time.monotonic() + timeout_sec
        last = "UNKNOWN"
        while time.monotonic() < deadline:
            info = self.get_session()
            last = info.get("_normalized_status") or normalize_status(info)
            if last in targets:
                return last
            time.sleep(interval_sec)
        return last

    def get_qr_json(self) -> dict:
        info = self.get_session()
        status = info.get("_normalized_status") or normalize_status(info)
        if status in CONNECTED_STATUSES:
            raise WahaError("ALREADY_CONNECTED")
        if status not in QR_READY_STATUSES:
            status = self.wait_for_status(QR_READY_STATUSES | CONNECTED_STATUSES)
            if status in CONNECTED_STATUSES:
                raise WahaError("ALREADY_CONNECTED")
        headers = self._headers(json_accept=True)
        headers["Accept"] = "application/json"
        url = f"{self.base}/api/{self.session_name}/auth/qr"
        if self.mock:
            return {"mimetype": "image/png", "data": "", "mock": True}
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code == 422:
            body = resp.text[:300]
            if "WORKING" in body.upper():
                raise WahaError("ALREADY_CONNECTED")
            raise WahaError("QR_NOT_READY")
        if resp.status_code >= 400:
            raise WahaError(f"QR {resp.status_code}: {resp.text[:200]}")
        return resp.json()

    def fetch_contacts(self) -> list[dict]:
        data = self._request("GET", "/api/contacts/all", params={"session": self.session_name})
        if isinstance(data, list):
            return data
        return data.get("contacts", data) if isinstance(data, dict) else []

    def send_text(self, chat_id: str, text: str) -> dict:
        return self._request(
            "POST",
            "/api/sendText",
            json={"session": self.session_name, "chatId": chat_id, "text": text},
        )

    def logout_session(self) -> dict:
        return self._request("POST", f"/api/sessions/{self.session_name}/logout", json={})

    def stop_session(self) -> dict:
        return self._request("POST", f"/api/sessions/{self.session_name}/stop", json={})

    def _mock(self, method: str, path: str, **kwargs) -> Any:
        if path == "/api/sessions" and method == "GET":
            return [{"name": self.session_name, "status": "WORKING"}]
        if path == f"/api/sessions/{self.session_name}":
            return {"name": self.session_name, "status": "WORKING"}
        if "/auth/qr" in path:
            return {"data": "", "mock": True}
        if path == "/api/contacts/all":
            return [
                {"id": "919876543210@c.us", "name": "Demo Contact A", "number": "919876543210"},
                {"id": "919876543211@c.us", "name": "Demo Contact B", "number": "919876543211"},
            ]
        if path == "/api/sendText":
            return {"mock": True, "sent": True, "payload": kwargs.get("json")}
        if path == "/api/sessions" and method == "POST":
            return {"name": self.session_name}
        if path.endswith("/start"):
            return {"status": "STARTING"}
        if path.endswith("/logout") or path.endswith("/stop"):
            return {"status": "STOPPED"}
        return {}
