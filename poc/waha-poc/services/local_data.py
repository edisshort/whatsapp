from extensions import db
from models import Campaign, CampaignMessage, Contact


def clear_all_local_data() -> dict:
    """Remove cached contacts and campaign history from SQLite."""
    msg_count = CampaignMessage.query.delete()
    camp_count = Campaign.query.delete()
    contact_count = Contact.query.delete()
    db.session.commit()
    return {
        "contacts": contact_count,
        "campaigns": camp_count,
        "messages": msg_count,
    }
