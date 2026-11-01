import re

import phonenumbers
from phonenumbers import PhoneNumberFormat, NumberParseException


def to_chat_id(phone: str, default_region: str = "IN") -> str | None:
    cleaned = re.sub(r"[^\d+]", "", phone or "")
    try:
        parsed = phonenumbers.parse(cleaned, default_region if not cleaned.startswith("+") else None)
        if not phonenumbers.is_valid_number(parsed):
            return None
        num = phonenumbers.format_number(parsed, PhoneNumberFormat.E164).lstrip("+")
        return f"{num}@c.us"
    except NumberParseException:
        return None


def chat_id_to_display(chat_id: str) -> str:
    if not chat_id:
        return ""
    return chat_id.replace("@c.us", "").replace("@s.whatsapp.net", "")
