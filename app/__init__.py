import os

from flask import Flask, render_template

from config import Config
from app.extensions import csrf, db, login_manager


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    os.makedirs(os.path.join(app.root_path, "..", "instance"), exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    from app import models  # noqa: F401

    from app.auth import auth_bp
    from app.main import main_bp
    from app.tickets import tickets_bp
    from app.admin import admin_bp
    from app.devices import devices_bp
    from app.chatbot import chatbot_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(tickets_bp, url_prefix="/talepler")
    app.register_blueprint(admin_bp, url_prefix="/yonetim")
    app.register_blueprint(devices_bp, url_prefix="/cihazlar")
    app.register_blueprint(chatbot_bp, url_prefix="/sss")

    @app.context_processor
    def inject_labels():
        return {
            "CATEGORY_LABELS": models.CATEGORY_LABELS,
            "PRIORITY_LABELS": models.PRIORITY_LABELS,
            "STATUS_LABELS": models.STATUS_LABELS,
            "PRIORITY_COLORS": models.PRIORITY_COLORS,
            "STATUS_COLORS": models.STATUS_COLORS,
        }

    @app.errorhandler(403)
    def forbidden(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    return app
