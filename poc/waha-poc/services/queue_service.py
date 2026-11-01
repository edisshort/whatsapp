import threading
import time

from datetime import datetime, timezone

from extensions import db
from models import Campaign, CampaignMessage, Contact
from services.waha_client import WahaClient, WahaError


def run_campaign(campaign_id: int, app) -> None:
    t = threading.Thread(target=_worker, args=(campaign_id, app), daemon=True)
    t.start()


def _worker(campaign_id: int, app) -> None:
    with app.app_context():
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return
        campaign.status = "running"
        db.session.commit()
        client = WahaClient()
        messages = CampaignMessage.query.filter_by(campaign_id=campaign_id, status="pending").all()
        for msg in messages:
            try:
                client.send_text(msg.chat_id, campaign.message_text)
                msg.status = "sent"
                msg.detail = "ok"
                msg.sent_at = datetime.now(timezone.utc)
            except WahaError as exc:
                msg.status = "failed"
                msg.detail = str(exc)[:480]
            db.session.commit()
            time.sleep(0.5)
        campaign.status = "completed"
        db.session.commit()
