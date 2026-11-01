import threading
import time
from datetime import datetime, timezone

from extensions import db
from models import Campaign, CampaignMessage
from services.evolution_client import EvolutionClient, EvolutionError
from services.phone_utils import chat_id_to_display


def run_campaign(campaign_id: int, app) -> None:
    threading.Thread(target=_worker, args=(campaign_id, app), daemon=True).start()


def _worker(campaign_id: int, app) -> None:
    with app.app_context():
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return
        campaign.status = "running"
        db.session.commit()
        client = EvolutionClient()
        messages = CampaignMessage.query.filter_by(campaign_id=campaign_id, status="pending").all()
        for msg in messages:
            phone = chat_id_to_display(msg.chat_id)
            try:
                client.send_text(phone, campaign.message_text)
                msg.status = "sent"
                msg.detail = "ok"
                msg.sent_at = datetime.now(timezone.utc)
            except EvolutionError as exc:
                msg.status = "failed"
                msg.detail = str(exc)[:480]
            db.session.commit()
            time.sleep(0.5)
        campaign.status = "completed"
        db.session.commit()
