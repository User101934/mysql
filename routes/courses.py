from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.models import db, Course, Enrollment, Certificate
from datetime import datetime, timezone
import uuid

courses_bp = Blueprint("courses", __name__, url_prefix="/api/courses")

@courses_bp.route("/", methods=["GET"])
def list_courses():
    category = request.args.get("category", "")
    search   = request.args.get("search", "")
    sort     = request.args.get("sort", "popular")
    page     = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 12))

    query = Course.query.filter_by(is_published=True)
    if category and category != "all":
        query = query.filter_by(category=category)
    if search:
        like = f"%{search}%"
        query = query.filter(db.or_(
            Course.title.ilike(like), Course.instructor.ilike(like)
        ))

    sort_map = {
        "popular":  Course.review_count.desc(),
        "newest":   Course.created_at.desc(),
        "rating":   Course.rating.desc(),
        "price-lo": Course.price.asc(),
        "price-hi": Course.price.desc(),
    }
    query = query.order_by(sort_map.get(sort, Course.review_count.desc()))
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "courses":     [c.to_dict() for c in pagination.items],
        "total":       pagination.total,
        "total_pages": pagination.pages,
    }), 200

@courses_bp.route("/<int:course_id>/enroll", methods=["POST"])
@jwt_required()
def enroll(course_id):
    user_id = int(get_jwt_identity())
    course  = Course.query.get_or_404(course_id)
    if Enrollment.query.filter_by(user_id=user_id, course_id=course_id).first():
        return jsonify({"error": "Already enrolled."}), 409
    e = Enrollment(user_id=user_id, course_id=course_id)
    db.session.add(e)
    db.session.commit()
    return jsonify({"message": f"Enrolled in {course.title}!", "enrollment": e.to_dict()}), 201

@courses_bp.route("/<int:course_id>/progress", methods=["PUT"])
@jwt_required()
def update_progress(course_id):
    user_id = int(get_jwt_identity())
    data    = request.get_json(silent=True) or {}
    e       = Enrollment.query.filter_by(user_id=user_id, course_id=course_id).first_or_404()

    if "lessons_completed" in data:
        e.lessons_completed = int(data["lessons_completed"])
    if "time_spent_minutes" in data:
        e.time_spent_minutes = int(data["time_spent_minutes"])

    if e.course.total_lessons:
        e.progress_percent = round((e.lessons_completed / e.course.total_lessons) * 100, 1)

    if e.progress_percent >= 100 and not e.completed_at:
        e.completed_at = datetime.now(timezone.utc)
        if not Certificate.query.filter_by(user_id=user_id, course_id=course_id).first():
            db.session.add(Certificate(
                user_id=user_id, course_id=course_id,
                certificate_code=f"NL-{uuid.uuid4().hex[:12].upper()}"
            ))
    db.session.commit()
    return jsonify({"message": "Progress updated.", "enrollment": e.to_dict()}), 200

@courses_bp.route("/my/enrolled", methods=["GET"])
@jwt_required()
def my_courses():
    user_id     = int(get_jwt_identity())
    enrollments = Enrollment.query.filter_by(user_id=user_id).all()
    return jsonify({"enrollments": [e.to_dict() for e in enrollments]}), 200