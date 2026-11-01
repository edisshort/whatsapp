from flask import Blueprint, flash, redirect, render_template, request, url_for

from config import Config
from routes.auth_helpers import login_required
from services.evolution_client import EvolutionClient, EvolutionError

connect_bp = Blueprint("connect", __name__, url_prefix="/connect")


@connect_bp.route("/")
@login_required
def index():
    status = "UNKNOWN"
    error = None
    try:
        info = EvolutionClient().get_session()
        status = info.get("status", "UNKNOWN")
    except EvolutionError as exc:
        error = str(exc)
    return render_template(
        "connect.html",
        status=status,
        qr_b64=None,
        error=error,
        session_name=Config.EVOLUTION_INSTANCE,
        engine=Config.ENGINE_LABEL,
        mock=Config.ENGINE_MOCK,
    )


@connect_bp.route("/start", methods=["POST"])
@login_required
def start():
    try:
        client = EvolutionClient()
        try:
            client.create_instance()
        except EvolutionError as exc:
            if "already" not in str(exc).lower():
                raise
        client.connect()
        flash("Instance created / connect requested. Load QR next.", "success")
    except EvolutionError as exc:
        flash(str(exc), "danger")
    return redirect(url_for("connect.index"))


@connect_bp.route("/qr")
@login_required
def qr():
    try:
        data = EvolutionClient().get_qr_payload()
        if Config.ENGINE_MOCK:
            flash("Mock mode: no QR needed.", "info")
            return redirect(url_for("connect.index"))
        b64 = data.get("base64") or data.get("qrcode", {}).get("base64") if isinstance(data.get("qrcode"), dict) else data.get("base64")
        if isinstance(b64, str) and b64.startswith("data:"):
            b64 = b64.split(",", 1)[-1]
        if b64:
            return render_template(
                "connect.html",
                status="SCAN_QR_CODE",
                qr_b64=b64,
                session_name=Config.EVOLUTION_INSTANCE,
                engine=Config.ENGINE_LABEL,
                mock=False,
            )
        flash(f"QR not in response. Keys: {list(data.keys()) if isinstance(data, dict) else 'n/a'}", "warning")
    except EvolutionError as exc:
        flash(str(exc), "danger")
    return redirect(url_for("connect.index"))


@connect_bp.route("/disconnect", methods=["POST"])
@login_required
def disconnect():
    clear_local = request.form.get("clear_local") == "yes"
    try:
        EvolutionClient().logout_instance()
        flash("WhatsApp instance logged out on Evolution API.", "success")
    except EvolutionError as exc:
        flash(f"Evolution disconnect: {exc}", "warning")
    if clear_local:
        from services.local_data import clear_all_local_data

        stats = clear_all_local_data()
        flash(f"Local cache cleared ({stats['contacts']} contacts).", "info")
    return redirect(url_for("connect.index"))
