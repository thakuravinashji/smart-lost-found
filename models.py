from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


# =========================================================
# USER MODEL
# =========================================================


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(150), unique=True, nullable=False)

    password = db.Column(db.String(255), nullable=False)

    phone = db.Column(db.String(20), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # =====================================================
    # USER → ITEMS
    # =====================================================

    items = db.relationship(
        "Item", backref="reporter", lazy=True, cascade="all, delete-orphan"
    )

    # =====================================================
    # USER → CLAIMS
    # =====================================================

    claims = db.relationship(
        "Claim", backref="claimant", lazy=True, cascade="all, delete-orphan"
    )

    # =====================================================
    # USER → NOTIFICATIONS
    # =====================================================

    notifications = db.relationship(
        "Notification", backref="user", lazy=True, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User {self.id} - {self.email}>"


# =========================================================
# ITEM MODEL
# =========================================================


class Item(db.Model):
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    name = db.Column(db.String(100), nullable=False)

    category = db.Column(db.String(100), nullable=False)

    description = db.Column(db.Text, nullable=False)

    location = db.Column(db.String(200), nullable=False)

    date = db.Column(db.String(20), nullable=False)

    item_type = db.Column(db.String(20), nullable=False)

    contact = db.Column(db.String(150), nullable=False)

    image = db.Column(db.String(255), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # =====================================================
    # ITEM → LOST CLAIMS
    # =====================================================

    lost_claims = db.relationship(
        "Claim", foreign_keys="Claim.lost_item_id", backref="lost_item", lazy=True
    )

    # =====================================================
    # ITEM → FOUND CLAIMS
    # =====================================================

    found_claims = db.relationship(
        "Claim", foreign_keys="Claim.found_item_id", backref="found_item", lazy=True
    )

    def __repr__(self):
        return f"<Item {self.id} - " f"{self.name} - " f"{self.item_type}>"


# =========================================================
# CLAIM MODEL
# =========================================================


class Claim(db.Model):
    __tablename__ = "claims"

    id = db.Column(db.Integer, primary_key=True)

    # =====================================================
    # CLAIMANT
    # =====================================================

    claimant_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # =====================================================
    # LOST ITEM
    # =====================================================

    lost_item_id = db.Column(db.Integer, db.ForeignKey("items.id"), nullable=False)

    # =====================================================
    # FOUND ITEM
    # =====================================================

    found_item_id = db.Column(db.Integer, db.ForeignKey("items.id"), nullable=False)

    # =====================================================
    # CLAIM MESSAGE
    # =====================================================

    message = db.Column(db.Text, nullable=True)

    # =====================================================
    # CLAIM STATUS
    # Pending / Approved / Rejected
    # =====================================================

    status = db.Column(db.String(20), default="Pending", nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Claim {self.id} - " f"{self.status}>"


# =========================================================
# NOTIFICATION MODEL
# =========================================================


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)

    # =====================================================
    # LINK NOTIFICATION → CLAIM
    # =====================================================

    claim_id = db.Column(db.Integer, db.ForeignKey("claims.id"), nullable=True)

    claim = db.relationship("Claim", backref="notifications")

    # =====================================================
    # USER RECEIVING NOTIFICATION
    # =====================================================

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # =====================================================
    # NOTIFICATION MESSAGE
    # =====================================================

    message = db.Column(db.Text, nullable=False)

    # =====================================================
    # NOTIFICATION TYPE
    #
    # general
    # match
    # claim
    # claim_approved
    # claim_rejected
    # message
    # =====================================================

    type = db.Column(db.String(50), nullable=False, default="general")

    # =====================================================
    # READ / UNREAD
    # =====================================================

    is_read = db.Column(db.Boolean, default=False, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Notification " f"{self.id} - " f"{self.user_id} - " f"{self.type}>"


# =========================================================
# MESSAGE MODEL
# =========================================================


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)

    # =====================================================
    # SENDER
    # =====================================================

    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # =====================================================
    # RECEIVER
    # =====================================================

    receiver_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # =====================================================
    # CLAIM
    # =====================================================

    claim_id = db.Column(db.Integer, db.ForeignKey("claims.id"), nullable=False)

    # =====================================================
    # MESSAGE TEXT
    # =====================================================

    message = db.Column(db.Text, nullable=False)

    # =====================================================
    # READ / UNREAD
    # =====================================================

    is_read = db.Column(db.Boolean, default=False, nullable=False)

    # =====================================================
    # CREATED TIME
    # Stored as UTC
    # =====================================================

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # =====================================================
    # RELATIONSHIPS
    # =====================================================

    sender = db.relationship("User", foreign_keys=[sender_id], backref="sent_messages")

    receiver = db.relationship(
        "User", foreign_keys=[receiver_id], backref="received_messages"
    )

    claim = db.relationship("Claim", backref="messages")

    def __repr__(self):
        return f"<Message " f"{self.id} - " f"Claim {self.claim_id}>"
