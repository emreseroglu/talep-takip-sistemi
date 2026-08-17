from datetime import datetime

from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.admin import admin_bp, statistics
from app.decorators import it_required
from app.extensions import db
from app.models import (
    CATEGORIES,
    PRIORITIES,
    STATUSES,
    Ticket,
    User,
)

TREND_DAYS = 30


@admin_bp.route("/")
@login_required
@it_required
def dashboard():
    status_counts = statistics.status_counts()
    stats = {
        "total": Ticket.query.count(),
        "users": User.query.count(),
        "avg_resolution": statistics.average_resolution_hours(),
    }
    for status in STATUSES:
        stats[status] = status_counts.get(status, 0)

    return render_template(
        "admin/dashboard.html",
        stats=stats,
        recent_tickets=Ticket.query.order_by(Ticket.created_at.desc()).limit(5).all(),
        category_data=statistics.category_distribution(),
        trend_data=statistics.daily_trend(days=TREND_DAYS),
        top_issues=statistics.top_issue_types(limit=5),
        resolution_by_category=statistics.resolution_by_category(),
        prediction_stats=statistics.prediction_accuracy(),
        trend_days=TREND_DAYS,
    )


@admin_bp.route("/talepler")
@login_required
@it_required
def ticket_list():
    filters = {
        "status": request.args.get("status", ""),
        "category": request.args.get("category", ""),
        "priority": request.args.get("priority", ""),
    }

    query = Ticket.query
    if filters["status"] in STATUSES:
        query = query.filter_by(status=filters["status"])
    if filters["category"] in CATEGORIES:
        query = query.filter_by(category=filters["category"])
    if filters["priority"] in PRIORITIES:
        query = query.filter_by(priority=filters["priority"])

    tickets = query.order_by(Ticket.created_at.desc()).all()

    return render_template(
        "admin/ticket_list.html",
        tickets=tickets,
        filters=filters,
        categories=CATEGORIES,
        priorities=PRIORITIES,
        statuses=STATUSES,
    )


@admin_bp.route("/talepler/<int:ticket_id>")
@login_required
@it_required
def ticket_detail(ticket_id):
    ticket = db.session.get(Ticket, ticket_id)
    if ticket is None:
        abort(404)
    return render_template("admin/ticket_detail.html", ticket=ticket)


@admin_bp.route("/talepler/<int:ticket_id>/durum", methods=["POST"])
@login_required
@it_required
def update_status(ticket_id):
    ticket = db.session.get(Ticket, ticket_id)
    if ticket is None:
        abort(404)

    new_status = request.form.get("status", "")
    if new_status not in STATUSES:
        flash("Geçersiz durum değeri.", "danger")
        return redirect(url_for("admin.ticket_detail", ticket_id=ticket.id))

    if new_status == ticket.status:
        flash("Talep zaten bu durumda.", "info")
        return redirect(url_for("admin.ticket_detail", ticket_id=ticket.id))

    ticket.status = new_status
    ticket.resolved_at = datetime.now() if new_status == "cozuldu" else None
    db.session.commit()

    flash(f"Talep #{ticket.id} durumu '{ticket.status_label}' olarak güncellendi.",
          "success")
    return redirect(url_for("admin.ticket_detail", ticket_id=ticket.id))
