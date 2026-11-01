from datetime import datetime, timezone

from extensions import db


class Contact(db.Model):
    __tablename__ = "contacts"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), default="")
    phone = db.Column(db.String(32), index=True)
    chat_id = db.Column(db.String(64), unique=True, index=True)
    selected = db.Column(db.Boolean, default=True)
    synced_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class Campaign(db.Model):
    __tablename__ = "campaigns"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    message_text = db.Column(db.Text)
    status = db.Column(db.String(32), default="draft")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class CampaignMessage(db.Model):
    __tablename__ = "campaign_messages"

    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey("campaigns.id"))
    contact_id = db.Column(db.Integer, db.ForeignKey("contacts.id"))
    chat_id = db.Column(db.String(64))
    status = db.Column(db.String(32), default="pending")
    detail = db.Column(db.String(500), default="")
    sent_at = db.Column(db.DateTime, nullable=True)

    campaign = db.relationship("Campaign", backref="messages")
    contact = db.relationship("Contact")
