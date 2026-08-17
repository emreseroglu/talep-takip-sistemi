from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.auth import auth_bp
from app.auth.forms import ChangePasswordForm, LoginForm
from app.extensions import db
from app.models import User


@auth_bp.route("/giris", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if user is None or not user.check_password(form.password.data):
            flash("E-posta veya şifre hatalı.", "danger")
            return render_template("auth/login.html", form=form)

        login_user(user, remember=form.remember_me.data)
        flash(f"Hoş geldiniz, {user.full_name}.", "success")

        next_page = request.args.get("next")
        if next_page and next_page.startswith("/") and not next_page.startswith("//"):
            return redirect(next_page)
        return redirect(url_for("main.index"))

    return render_template("auth/login.html", form=form)


@auth_bp.route("/cikis")
@login_required
def logout():
    logout_user()
    flash("Oturumunuz kapatıldı.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/profil", methods=["GET", "POST"])
@login_required
def profile():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash("Mevcut şifreniz hatalı.", "danger")
        else:
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash("Şifreniz güncellendi.", "success")
            return redirect(url_for("auth.profile"))
    return render_template("auth/profile.html", form=form)
