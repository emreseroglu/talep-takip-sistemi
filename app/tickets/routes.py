from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.ml.classifier import classify
from app.models import Ticket
from app.tickets import tickets_bp
from app.tickets.forms import TicketForm


@tickets_bp.route("/")
@login_required
def my_tickets():
    tickets = (
        Ticket.query.filter_by(user_id=current_user.id)
        .order_by(Ticket.created_at.desc())
        .all()
    )
    return render_template("tickets/my_tickets.html", tickets=tickets)


@tickets_bp.route("/yeni", methods=["GET", "POST"])
@login_required
def new_ticket():
    form = TicketForm()

    if request.method == "GET":
        device_id = request.args.get("cihaz", "")
        if device_id in dict(form.device_id.choices):
            form.device_id.data = device_id

    if form.validate_on_submit():
        title = form.title.data.strip()
        description = form.description.data.strip()

        prediction = classify(title, description)

        ticket = Ticket(
            user_id=current_user.id,
            title=title,
            description=description,
            category=form.category.data,
            priority=form.priority.data,
            status="acik",
            device_id=int(form.device_id.data) if form.device_id.data != "0" else None,
            predicted_category=prediction["category"],
            predicted_priority=prediction["priority"],
            category_confidence=prediction["category_confidence"],
            priority_confidence=prediction["priority_confidence"],
        )
        db.session.add(ticket)
        db.session.commit()

        flash(f"Talebiniz #{ticket.id} numarasıyla oluşturuldu.", "success")
        return redirect(url_for("tickets.ticket_detail", ticket_id=ticket.id))

    return render_template("tickets/new_ticket.html", form=form)


@tickets_bp.route("/<int:ticket_id>")
@login_required
def ticket_detail(ticket_id):
    ticket = db.session.get(Ticket, ticket_id)
    if ticket is None:
        abort(404)

    if ticket.user_id != current_user.id and not current_user.is_it_staff:
        abort(403)

    return render_template("tickets/ticket_detail.html", ticket=ticket)
