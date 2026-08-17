from functools import wraps

from flask import abort, flash, redirect, url_for
from flask_login import current_user


def it_required(view_func):

    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))
        if not current_user.is_it_staff:
            flash("Bu sayfaya erişim yetkiniz bulunmuyor.", "danger")
            return abort(403)
        return view_func(*args, **kwargs)

    return wrapper
