from flask import Blueprint

tickets_bp = Blueprint("tickets", __name__)

from app.tickets import routes  # noqa: E402,F401
