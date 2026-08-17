from flask import jsonify, request, url_for
from flask_login import login_required

from app.chatbot import chatbot_bp
from app.ml.faq import get_matcher

MAX_MESSAGE_LENGTH = 500


@chatbot_bp.route("/sor", methods=["POST"])
@login_required
def ask():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", ""))[:MAX_MESSAGE_LENGTH].strip()

    if not message:
        return jsonify({
            "found": False,
            "results": [],
            "message": "Lütfen bir soru yazınız.",
        })

    results = get_matcher().search(message)

    if not results:
        return jsonify({
            "found": False,
            "results": [],
            "message": ("Bu konuda size yardımcı olamadım. "
                        "Bir talep oluşturmanızı öneririm."),
            "ticket_url": url_for("tickets.new_ticket"),
        })

    return jsonify({"found": True, "results": results})


@chatbot_bp.route("/sorular")
@login_required
def suggestions():
    entries = get_matcher().entries
    return jsonify({
        "questions": [e["question"] for e in entries[:4]],
    })
