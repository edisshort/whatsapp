from flask import Blueprint, flash, redirect, render_template, request, url_for

from extensions import db
from models import Contact
from routes.auth_helpers import login_required
from services.contact_sync import sync_contacts_from_engine
from services.waha_client import WahaError

contacts_bp = Blueprint("contacts", __name__, url_prefix="/contacts")


@contacts_bp.route("/")
@login_required
def index():
    rows = Contact.query.order_by(Contact.name).limit(500).all()
    return render_template("contacts.html", contacts=rows)


@contacts_bp.route("/sync", methods=["POST"])
@login_required
def sync():
    try:
        total = sync_contacts_from_engine()
        flash(f"Synced contacts. Total in database: {total}", "success")
    except WahaError as exc:
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
