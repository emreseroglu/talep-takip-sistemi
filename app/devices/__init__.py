from flask import Blueprint

devices_bp = Blueprint("devices", __name__)

from app.devices import routes  # noqa: E402,F401
