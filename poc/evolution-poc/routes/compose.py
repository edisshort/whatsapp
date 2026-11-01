from flask import Blueprint, flash, redirect, render_template, request, url_for

from extensions import db
from models import Campaign, CampaignMessage, Contact
from routes.auth_helpers import login_required
from services.evolution_client import EvolutionClient, EvolutionError
from services.phone_utils import chat_id_to_display
from services.queue_service import run_campaign

compose_bp = Blueprint("compose", __name__)


@compose_bp.route("/compose", methods=["GET", "POST"])
@login_required
def compose():
    contacts = Contact.query.order_by(Contact.name).all()
    if request.method == "POST":
        action = request.form.get("action")
        text = request.form.get("message", "").strip()
        chat_id = request.form.get("chat_id")
        if action == "single" and text and chat_id:
            phone = chat_id_to_display(chat_id)
            try:
                EvolutionClient().send_text(phone, text)
                flash("Message sent.", "success")
            except EvolutionError as exc:
                flash(str(exc), "danger")
            return redirect(url_for("compose.compose"))
        if action == "campaign" and text:
            name = request.form.get("campaign_name", "Campaign") or "Campaign"
            ids = [int(x) for x in request.form.getlist("contact_ids") if x.isdigit()]
            if not ids:
                flash("Select at least one contact.", "warning")
                return redirect(url_for("compose.compose"))
            selected = Contact.query.filter(Contact.id.in_(ids)).all()
            if not selected:
                flash("Select at least one contact.", "warning")
                return redirect(url_for("compose.compose"))
            camp = Campaign(name=name, message_text=text, status="queued")
            db.session.add(camp)
            db.session.flush()
            for c in selected:
                db.session.add(
                    CampaignMessage(
                        campaign_id=camp.id,
                        contact_id=c.id,
                        chat_id=c.chat_id,
                        status="pending",
                    )
                )
            db.session.commit()
            from flask import current_app

            run_campaign(camp.id, current_app._get_current_object())
            flash(f"Campaign queued for {len(selected)} recipients.", "success")
            return redirect(url_for("campaigns.detail", campaign_id=camp.id))
    return render_template("compose.html", contacts=contacts)


campaigns_bp = Blueprint("campaigns", __name__, url_prefix="/campaigns")


@campaigns_bp.route("/")
@login_required
def list_campaigns():
    items = Campaign.query.order_by(Campaign.created_at.desc()).all()
    return render_template("campaigns.html", campaigns=items)


@campaigns_bp.route("/<int:campaign_id>")
@login_required
def detail(campaign_id):
    camp = Campaign.query.get_or_404(campaign_id)
    messages = CampaignMessage.query.filter_by(campaign_id=campaign_id).all()
    return render_template("campaign_detail.html", campaign=camp, messages=messages)
