from flask import redirect, render_template, url_for
from flask_login import current_user, login_required

from app.main import main_bp


@main_bp.route("/")
@login_required
def index():
    if current_user.is_it_staff:
        return redirect(url_for("admin.dashboard"))
    return redirect(url_for("tickets.my_tickets"))


@main_bp.route("/hakkinda")
def about():
    return render_template("main/about.html")
