from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.models import Enrollment, Certificate

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")

@dashboard_bp.route("/stats", methods=["GET"])
@jwt_required()
def get_stats():
    user_id      = int(get_jwt_identity())
    enrollments  = Enrollment.query.filter_by(user_id=user_id).all()
    certificates = Certificate.query.filter_by(user_id=user_id).all()
    total_time   = sum(e.time_spent_minutes for e in enrollments)
    completed    = [e for e in enrollments if e.completed_at]

    return jsonify({
        "courses_enrolled":    len(enrollments),
        "courses_completed":   len(completed),
        "certificates_earned": len(certificates),
        "total_hours":         round(total_time / 60, 1),
        "enrollments":         [e.to_dict() for e in enrollments],
        "certificates":        [c.to_dict() for c in certificates],
    }), 200