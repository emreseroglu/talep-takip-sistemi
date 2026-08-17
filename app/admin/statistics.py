from collections import Counter
from datetime import date, datetime, timedelta

from sqlalchemy import func

from app.extensions import db
from app.ml.preprocessing import normalize_text
from app.models import CATEGORIES, CATEGORY_LABELS, Ticket

ISSUE_TYPES = [
    ("Yazıcı / Tarayıcı", ["yazıc", "toner", "kartuş", "fotokopi", "tarayıc", "çıktı"]),
    ("İnternet / Ağ", ["internet", "kablosuz", "wifi", "modem", "vpn", "bağlantı",
                       "ağ ", "ağa", "ağda", "sunucu"]),
    ("Hesap / Şifre / Yetki", ["şifre", "parola", "hesab", "hesap", "yetki",
                               "giriş yap", "ebys", "kullanıcı hesab"]),
    ("Ofis / Yazılım", ["excel", "word", "outlook", "office", "ofis", "program",
                        "yazılım", "uygulama", "lisans", "kurulum", "sürücü", "virüs"]),
    ("Bilgisayar / Donanım", ["bilgisayar", "kasa", "ekran", "monitör", "klavye",
                              "mouse", "fare", "disk", "hoparlör", "kamera"]),
]


def status_counts() -> dict:
    rows = db.session.query(Ticket.status, func.count(Ticket.id)).group_by(
        Ticket.status).all()
    return dict(rows)


def category_distribution() -> dict:
    rows = dict(db.session.query(Ticket.category, func.count(Ticket.id))
                .group_by(Ticket.category).all())
    return {
        "labels": [CATEGORY_LABELS[c] for c in CATEGORIES],
        "values": [rows.get(c, 0) for c in CATEGORIES],
    }


def daily_trend(days: int = 30) -> dict:
    today = date.today()
    start = today - timedelta(days=days - 1)
    start_dt = datetime.combine(start, datetime.min.time())

    opened = Counter()
    resolved = Counter()

    for ticket in Ticket.query.filter(Ticket.created_at >= start_dt).all():
        opened[ticket.created_at.date()] += 1

    for ticket in Ticket.query.filter(Ticket.resolved_at.isnot(None),
                                      Ticket.resolved_at >= start_dt).all():
        resolved[ticket.resolved_at.date()] += 1

    labels, opened_series, resolved_series = [], [], []
    for offset in range(days):
        day = start + timedelta(days=offset)
        labels.append(day.strftime("%d.%m"))
        opened_series.append(opened.get(day, 0))
        resolved_series.append(resolved.get(day, 0))

    return {"labels": labels, "opened": opened_series, "resolved": resolved_series}


def average_resolution_hours():
    tickets = Ticket.query.filter(Ticket.resolved_at.isnot(None)).all()
    if not tickets:
        return None
    total = sum((t.resolved_at - t.created_at).total_seconds() for t in tickets)
    return round(total / len(tickets) / 3600, 1)


def resolution_by_category() -> dict:
    totals, counts = Counter(), Counter()
    for t in Ticket.query.filter(Ticket.resolved_at.isnot(None)).all():
        totals[t.category] += (t.resolved_at - t.created_at).total_seconds() / 3600
        counts[t.category] += 1
    return {
        CATEGORY_LABELS[c]: round(totals[c] / counts[c], 1) if counts[c] else 0
        for c in CATEGORIES
    }


def top_issue_types(limit: int = 5) -> dict:
    counts = Counter()
    for title, description in db.session.query(Ticket.title, Ticket.description).all():
        text = normalize_text(f"{title} {description}")
        for issue_type, roots in ISSUE_TYPES:
            if any(root in text for root in roots):
                counts[issue_type] += 1
                break
        else:
            counts["Diğer"] += 1

    top = counts.most_common(limit)
    return {
        "labels": [name for name, _ in top],
        "values": [value for _, value in top],
    }


def prediction_accuracy() -> dict:
    tickets = Ticket.query.filter(Ticket.predicted_category.isnot(None)).all()
    if not tickets:
        return {"total": 0, "category_match": 0, "priority_match": 0, "mismatch": 0}

    return {
        "total": len(tickets),
        "category_match": sum(1 for t in tickets if not t.category_mismatch),
        "priority_match": sum(1 for t in tickets if not t.priority_mismatch),
        "mismatch": sum(1 for t in tickets if t.has_mismatch),
    }
