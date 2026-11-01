from datetime import datetime, timezone

from extensions import db
from models import Contact
from services.evolution_client import EvolutionClient
from services.phone_utils import chat_id_to_display, to_chat_id


def _normalize_chat_id(item: dict) -> tuple[str, str, str]:
    # Evolution stores DB id in "id"; WhatsApp JID is in "remoteJid"
    raw_id = item.get("remoteJid") or item.get("id") or ""
    if "@" not in raw_id:
        raw_id = ""
    name = item.get("pushName") or item.get("name") or ""
    if raw_id.endswith("@s.whatsapp.net") or raw_id.endswith("@c.us"):
        phone = chat_id_to_display(raw_id.replace("@s.whatsapp.net", "@c.us"))
        chat_id = raw_id.replace("@s.whatsapp.net", "@c.us")
        return name or phone, phone, chat_id
    phone_raw = str(item.get("number", "") or "")
    chat_id = to_chat_id(phone_raw) or f"{phone_raw}@c.us"
    phone = chat_id_to_display(chat_id)
    return name or phone, phone, chat_id


def sync_contacts_from_engine() -> int:
    client = EvolutionClient()
    raw = client.fetch_contacts()
    for item in raw:
        if item.get("isGroup") or str(item.get("remoteJid", "")).endswith("@g.us"):
            continue
        name, phone, chat_id = _normalize_chat_id(item)
        if not chat_id:
            continue
        row = Contact.query.filter_by(chat_id=chat_id).first()
        if row:
            row.name = name
            row.phone = phone
            row.synced_at = datetime.now(timezone.utc)
        else:
            db.session.add(Contact(name=name, phone=phone, chat_id=chat_id))
    db.session.commit()
    return Contact.query.count()
