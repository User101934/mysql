from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()

from config.config import Config
from models.models import db
from routes.auth      import auth_bp
from routes.courses   import courses_bp
from routes.dashboard import dashboard_bp
from routes.contact   import contact_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(
        hours=Config.JWT_ACCESS_TOKEN_EXPIRES_HOURS
    )

    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": Config.ALLOWED_ORIGINS}})
    jwt = JWTManager(app)

    @jwt.unauthorized_loader
    def missing_token(reason):
        return jsonify({"error": "Login required."}), 401

    @jwt.expired_token_loader
    def expired_token(header, payload):
        return jsonify({"error": "Session expired. Please log in again."}), 401

    app.register_blueprint(auth_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(contact_bp)

    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok", "service": "NexLearn API"}), 200

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found."}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Server error."}), 500

    return app

def seed_courses(app):
    from models.models import Course
    with app.app_context():
        if Course.query.count() > 0:
            print("✅ Courses already seeded.")
            return
        courses = [
            dict(title="Python for Data Science & AI", slug="python-data-science-ai",
                 instructor="Dr. Sarah Chen", category="tech", tag="Python", emoji="🐍",
                 level="Beginner", price=89, original_price=149,
                 total_lessons=48, total_hours=32, rating=4.9, review_count=8420),
            dict(title="AWS Solutions Architect 2026", slug="aws-solutions-architect",
                 instructor="Mark Rivera", category="cloud", tag="Cloud", emoji="☁️",
                 level="Intermediate", price=119, original_price=189,
                 total_lessons=62, total_hours=45, rating=4.8, review_count=6130),
            dict(title="UI/UX Design Bootcamp", slug="ui-ux-design-bootcamp",
                 instructor="Priya Sharma", category="design", tag="Design", emoji="🎨",
                 level="All Levels", price=99, original_price=159,
                 total_lessons=55, total_hours=38, rating=4.9, review_count=12040),
            dict(title="React & Next.js 15 Complete", slug="react-nextjs-complete",
                 instructor="Kevin Park", category="tech", tag="React", emoji="⚛️",
                 level="Intermediate", price=109, original_price=179,
                 total_lessons=72, total_hours=54, rating=4.8, review_count=9210),
            dict(title="Business Analytics with Power BI", slug="business-analytics-power-bi",
                 instructor="Emma Wilson", category="data", tag="Data", emoji="📈",
                 level="Beginner", price=79, original_price=129,
                 total_lessons=40, total_hours=28, rating=4.7, review_count=4320),
            dict(title="Machine Learning A-Z", slug="machine-learning-az",
                 instructor="Dr. Maria Santos", category="data", tag="ML", emoji="📊",
                 level="All Levels", price=99, original_price=169,
                 total_lessons=85, total_hours=62, rating=4.8, review_count=18200),
            dict(title="Full Stack Web Dev Bootcamp", slug="full-stack-web-dev",
                 instructor="Tom Bradley", category="tech", tag="Full Stack", emoji="🖥️",
                 level="All Levels", price=149, original_price=249,
                 total_lessons=120, total_hours=90, rating=4.7, review_count=22100),
            dict(title="Digital Marketing Masterclass", slug="digital-marketing-masterclass",
                 instructor="James Horner", category="marketing", tag="Marketing", emoji="📣",
                 level="Beginner", price=69, original_price=119,
                 total_lessons=44, total_hours=31, rating=4.6, review_count=5410),
        ]
        for c in courses:
            db.session.add(Course(**c))
        db.session.commit()
        print(f"✅ Seeded {len(courses)} courses.")

def init_db(app):
    with app.app_context():
        try:
            # Check connection
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
            
            # Create tables and seed
            db.create_all()
            seed_courses(app)
            print("✅ Database initialized successfully.")
        except Exception as e:
            app.logger.error(f"❌ Database initialization failed: {e}")

# Initialize app and database
app = create_app()
init_db(app)





if __name__ == "__main__":
    # ── Print DB connection so we can debug ──────────────
    print("🔌 Connecting to:", app.config["SQLALCHEMY_DATABASE_URI"])

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
