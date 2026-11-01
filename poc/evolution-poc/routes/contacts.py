from flask import Blueprint, flash, redirect, url_for

from routes.auth_helpers import login_required
from services.contact_sync import sync_contacts_from_engine
from services.evolution_client import EvolutionError

contacts_bp = Blueprint("contacts", __name__, url_prefix="/contacts")


@contacts_bp.route("/")
@login_required
def index():
    from flask import render_template
    from models import Contact

    rows = Contact.query.order_by(Contact.name).limit(500).all()
    return render_template("contacts.html", contacts=rows)


@contacts_bp.route("/sync", methods=["POST"])
@login_required
def sync():
    try:
        total = sync_contacts_from_engine()
        flash(f"Synced contacts. Total in database: {total}", "success")
    except EvolutionError as exc:
        flash(str(exc), "danger")
    return redirect(url_for("contacts.index"))


@contacts_bp.route("/clear", methods=["POST"])
@login_required
def clear():
    from services.local_data import clear_all_local_data

    stats = clear_all_local_data()
    flash(
        f"Cleared local cache: {stats['contacts']} contacts, "
        f"{stats['campaigns']} campaigns, {stats['messages']} message rows.",
        "success",
    )
    return redirect(url_for("contacts.index"))
