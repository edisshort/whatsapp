from flask import Blueprint, flash, redirect, render_template, request, url_for

from config import Config
from routes.auth_helpers import login_required
from services.waha_client import (
    CONNECTED_STATUSES,
    QR_READY_STATUSES,
    WahaClient,
    WahaError,
    normalize_status,
)

connect_bp = Blueprint("connect", __name__, url_prefix="/connect")


def _connect_context(client: WahaClient | None = None, **extra):
    status = "UNKNOWN"
    error = None
    connected = False
    try:
        client = client or WahaClient()
        info = client.get_session()
        status = info.get("_normalized_status") or normalize_status(info)
        connected = status in CONNECTED_STATUSES
    except WahaError as exc:
        error = str(exc)
    ctx = {
        "status": status,
        "qr_b64": None,
        "error": error,
        "connected": connected,
        "can_load_qr": status in QR_READY_STATUSES and not connected,
        "session_name": Config.WAHA_SESSION,
        "engine": Config.ENGINE_LABEL,
        "mock": Config.ENGINE_MOCK,
    }
    ctx.update(extra)
    return ctx


@connect_bp.route("/")
@login_required
def index():
    return render_template("connect.html", **_connect_context())


@connect_bp.route("/start", methods=["POST"])
@login_required
def start():
    try:
        client = WahaClient()
        info = client.get_session()
        status = info.get("_normalized_status") or normalize_status(info)
        if status in CONNECTED_STATUSES:
            flash("WhatsApp is already connected.", "info")
            return redirect(url_for("connect.index"))
        client.start_session()
        flash("Session starting… wait until status is SCAN_QR_CODE, then load QR.", "success")
    except WahaError as exc:
        flash(str(exc), "danger")
    return redirect(url_for("connect.index"))


def _friendly_qr_error(exc: WahaError) -> tuple[str, str]:
    msg = str(exc)
    if msg == "ALREADY_CONNECTED":
        return (
            "WhatsApp is already linked (status WORKING). No QR needed — go to Contacts → Sync.",
            "success",
        )
    if msg == "QR_NOT_READY":
        return (
            "QR is not ready yet. Wait a few seconds after Start session, then try Load QR again.",
            "warning",
        )
    if "422" in msg and "WORKING" in msg.upper():
        return (
            "WhatsApp is already linked. Disconnect first if you want to scan a new QR.",
            "info",
        )
    return (msg, "danger")


@connect_bp.route("/qr")
@login_required
def qr():
    try:
        client = WahaClient()
        info = client.get_session()
        status = info.get("_normalized_status") or normalize_status(info)
        if status in CONNECTED_STATUSES:
            flash("WhatsApp is already connected.", "success")
            return redirect(url_for("connect.index"))
        if Config.ENGINE_MOCK:
            flash("Mock mode: scan not required — status is WORKING.", "info")
            return redirect(url_for("connect.index"))
        data = client.get_qr_json()
        b64 = data.get("data") or data.get("base64") or ""
        if b64:
            ctx = _connect_context(client, status="SCAN_QR_CODE", qr_b64=b64, can_load_qr=True)
            return render_template("connect.html", **ctx)
        flash("No QR in response — wait and try again.", "warning")
    except WahaError as exc:
        text, category = _friendly_qr_error(exc)
        flash(text, category)
    return redirect(url_for("connect.index"))


@connect_bp.route("/disconnect", methods=["POST"])
@login_required
def disconnect():
    clear_local = request.form.get("clear_local") == "yes"
    try:
        client = WahaClient()
        try:
            client.logout_session()
        except WahaError:
            pass
        try:
            client.stop_session()
        except WahaError:
            pass
        flash("WhatsApp disconnected on WAHA. Click Start session to link again.", "success")
    except WahaError as exc:
        flash(f"WAHA disconnect: {exc}", "warning")
    if clear_local:
        from services.local_data import clear_all_local_data

        stats = clear_all_local_data()
        flash(f"Local cache cleared ({stats['contacts']} contacts).", "info")
    return redirect(url_for("connect.index"))
