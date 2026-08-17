from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db, login_manager


ROLE_STAFF = "personel"
ROLE_IT = "bilgi_islem"

CATEGORIES = ["donanim", "yazilim", "ag", "diger"]
PRIORITIES = ["dusuk", "orta", "yuksek"]
STATUSES = ["acik", "islemde", "cozuldu"]

CATEGORY_LABELS = {
    "donanim": "Donanım",
    "yazilim": "Yazılım",
    "ag": "Ağ / İnternet",
    "diger": "Diğer",
}
PRIORITY_LABELS = {"dusuk": "Düşük", "orta": "Orta", "yuksek": "Yüksek"}
STATUS_LABELS = {"acik": "Açık", "islemde": "İşlemde", "cozuldu": "Çözüldü"}
ROLE_LABELS = {ROLE_STAFF: "Personel", ROLE_IT: "Bilgi İşlem"}

PRIORITY_COLORS = {"dusuk": "secondary", "orta": "warning", "yuksek": "danger"}
STATUS_COLORS = {"acik": "danger", "islemde": "warning", "cozuldu": "success"}


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    department = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=ROLE_STAFF)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    tickets = db.relationship(
        "Ticket", back_populates="user", cascade="all, delete-orphan"
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_it_staff(self) -> bool:
        return self.role == ROLE_IT

    @property
    def role_label(self) -> str:
        return ROLE_LABELS.get(self.role, self.role)

    def __repr__(self) -> str:
        return f"<User {self.id} {self.full_name} ({self.role})>"


class Ticket(db.Model):
    __tablename__ = "tickets"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    device_id = db.Column(db.Integer, db.ForeignKey("devices.id"), nullable=True)

    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)

    category = db.Column(db.String(20), nullable=False, default="diger")
    priority = db.Column(db.String(20), nullable=False, default="orta")
    status = db.Column(db.String(20), nullable=False, default="acik")

    predicted_category = db.Column(db.String(20), nullable=True)
    predicted_priority = db.Column(db.String(20), nullable=True)
    category_confidence = db.Column(db.Float, nullable=True)
    priority_confidence = db.Column(db.Float, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(
        db.DateTime, default=datetime.now, onupdate=datetime.now
    )
    resolved_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User", back_populates="tickets")
    device = db.relationship("Device", back_populates="tickets")

    @property
    def category_label(self) -> str:
        return CATEGORY_LABELS.get(self.category, self.category)

    @property
    def priority_label(self) -> str:
        return PRIORITY_LABELS.get(self.priority, self.priority)

    @property
    def status_label(self) -> str:
        return STATUS_LABELS.get(self.status, self.status)

    @property
    def predicted_category_label(self) -> str:
        return CATEGORY_LABELS.get(self.predicted_category, "-")

    @property
    def predicted_priority_label(self) -> str:
        return PRIORITY_LABELS.get(self.predicted_priority, "-")

    @property
    def category_mismatch(self) -> bool:
        return (self.predicted_category is not None
                and self.predicted_category != self.category)

    @property
    def priority_mismatch(self) -> bool:
        return (self.predicted_priority is not None
                and self.predicted_priority != self.priority)

    @property
    def has_mismatch(self) -> bool:
        return self.category_mismatch or self.priority_mismatch

    @property
    def resolution_hours(self):
        if self.resolved_at is None:
            return None
        delta = self.resolved_at - self.created_at
        return round(delta.total_seconds() / 3600, 1)

    def __repr__(self) -> str:
        return f"<Ticket #{self.id} {self.title[:20]} ({self.status})>"


class Device(db.Model):
    __tablename__ = "devices"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    assigned_to = db.Column(db.String(120), nullable=False)
    serial_no = db.Column(db.String(80), unique=True, nullable=False)
    location = db.Column(db.String(120), nullable=True)
    registered_at = db.Column(db.DateTime, default=datetime.now)

    tickets = db.relationship("Ticket", back_populates="device")

    @property
    def fault_count(self) -> int:
        return len(self.tickets)

    @property
    def open_tickets(self) -> list:
        return [t for t in self.tickets if t.status != "cozuldu"]

    @property
    def ticket_history(self) -> list:
        return sorted(self.tickets, key=lambda t: t.created_at, reverse=True)

    @property
    def label(self) -> str:
        return f"{self.serial_no} — {self.name}"

    def __repr__(self) -> str:
        return f"<Device {self.id} {self.name} ({self.serial_no})>"


@login_manager.user_loader
def load_user(user_id: str):
    return db.session.get(User, int(user_id))
