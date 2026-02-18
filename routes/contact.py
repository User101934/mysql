from flask import Blueprint, request, jsonify
from models.models import db, ContactMessage

contact_bp = Blueprint("contact", __name__, url_prefix="/api/contact")

@contact_bp.route("/", methods=["POST"])
def send_message():
    data       = request.get_json(silent=True) or {}
    first_name = data.get("first_name", "").strip()
    last_name  = data.get("last_name", "").strip()
    email      = data.get("email", "").strip()
    message    = data.get("message", "").strip()
    topic      = data.get("topic", "General")
    company    = data.get("company", "") or None

    if not all([first_name, email, message]):
        return jsonify({"error": "Please fill all required fields."}), 400

    msg = ContactMessage(
        first_name=first_name, last_name=last_name,
        email=email, company=company, topic=topic, message=message
    )
    db.session.add(msg)
    db.session.commit()
    return jsonify({"message": "Message received! We'll reply within 24h."}), 201