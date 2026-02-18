from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import bcrypt
from datetime import timedelta
from models.models import db, User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

def hash_password(plain):
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()

def check_password(plain, hashed):
    return bcrypt.checkpw(plain.encode(), hashed.encode())

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    first_name = data.get("first_name", "").strip()
    last_name  = data.get("last_name", "").strip()
    email      = data.get("email", "").strip().lower()
    password   = data.get("password", "")

    if not all([first_name, last_name, email, password]):
        return jsonify({"error": "All fields are required."}), 400
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters."}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered."}), 409

    user = User(
        first_name=first_name, last_name=last_name,
        email=email, password_hash=hash_password(password)
    )
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id), expires_delta=timedelta(hours=24))
    return jsonify({"message": "Account created!", "token": token, "user": user.to_dict()}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email    = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password required."}), 400

    user = User.query.filter_by(email=email, is_active=True).first()
    if not user or not check_password(password, user.password_hash):
        return jsonify({"error": "Invalid email or password."}), 401

    token = create_access_token(identity=str(user.id), expires_delta=timedelta(hours=24))
    return jsonify({"message": "Login successful.", "token": token, "user": user.to_dict()}), 200

@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_me():
    user = User.query.get_or_404(int(get_jwt_identity()))
    return jsonify({"user": user.to_dict()}), 200

@auth_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    user = User.query.get_or_404(int(get_jwt_identity()))
    data = request.get_json(silent=True) or {}
    for field in ["first_name", "last_name", "bio", "learning_goal", "avatar_url"]:
        if field in data:
            setattr(user, field, data[field])
    db.session.commit()
    return jsonify({"message": "Profile updated.", "user": user.to_dict()}), 200