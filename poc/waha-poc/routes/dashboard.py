from flask import Blueprint, render_template

from config import Config
from extensions import db
from models import Campaign, CampaignMessage, Contact
from routes.auth_helpers import login_required
from services.waha_client import WahaClient

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    health = WahaClient().health()
    session_info = {}
    try:
        session_info = WahaClient().get_session()
    except Exception:
        pass
    return render_template(
        "dashboard.html",
        contacts=Contact.query.count(),
        campaigns=Campaign.query.count(),
        sent=CampaignMessage.query.filter_by(status="sent").count(),
        failed=CampaignMessage.query.filter_by(status="failed").count(),
        engine=Config.ENGINE_LABEL,
        engine_url=Config.WAHA_BASE_URL,
        health=health,
        session_info=session_info,
        mock=Config.ENGINE_MOCK,
    )
