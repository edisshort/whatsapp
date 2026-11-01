from datetime import datetime, timezone

from extensions import db
from models import Contact
from services.phone_utils import chat_id_to_display
from services.waha_client import WahaClient


def sync_contacts_from_engine() -> int:
    client = WahaClient()
    raw = client.fetch_contacts()
    count = 0
    for item in raw:
        chat_id = item.get("id") or item.get("chatId") or ""
        if not chat_id:
            num = str(item.get("number", "") or item.get("phone", ""))
            if num:
                chat_id = f"{num.lstrip('+')}@c.us"
        if not chat_id:
            continue
        name = item.get("name") or item.get("pushname") or chat_id_to_display(chat_id)
        phone = chat_id_to_display(chat_id)
        row = Contact.query.filter_by(chat_id=chat_id).first()
        if row:
            row.name = name
            row.phone = phone
            row.synced_at = datetime.now(timezone.utc)
        else:
            db.session.add(Contact(name=name, phone=phone, chat_id=chat_id))
            count += 1
    db.session.commit()
    return Contact.query.count()
