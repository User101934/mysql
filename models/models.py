from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    id            = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name    = db.Column(db.String(80), nullable=False)
    last_name     = db.Column(db.String(80), nullable=False)
    email         = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    avatar_url    = db.Column(db.String(500), nullable=True)
    bio           = db.Column(db.Text, nullable=True)
    learning_goal = db.Column(db.String(100), nullable=True)
    plan          = db.Column(db.String(20), nullable=False, default="starter")
    is_active     = db.Column(db.Boolean, default=True)
    created_at    = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    enrollments  = db.relationship("Enrollment", back_populates="user", lazy="dynamic")
    certificates = db.relationship("Certificate", back_populates="user", lazy="dynamic")
    contact_msgs = db.relationship("ContactMessage", back_populates="user", lazy="dynamic")

    def to_dict(self):
        return {
            "id":            self.id,
            "first_name":    self.first_name,
            "last_name":     self.last_name,
            "full_name":     f"{self.first_name} {self.last_name}",
            "email":         self.email,
            "avatar_url":    self.avatar_url,
            "bio":           self.bio,
            "learning_goal": self.learning_goal,
            "plan":          self.plan,
            "created_at":    self.created_at.isoformat() if self.created_at else None,
        }

class Course(db.Model):
    __tablename__ = "courses"
    id             = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title          = db.Column(db.String(255), nullable=False)
    slug           = db.Column(db.String(255), unique=True, nullable=False)
    description    = db.Column(db.Text, nullable=True)
    instructor     = db.Column(db.String(120), nullable=False)
    category       = db.Column(db.String(60), nullable=False)
    tag            = db.Column(db.String(60), nullable=True)
    emoji          = db.Column(db.String(10), nullable=True)
    level          = db.Column(db.String(30), nullable=False, default="All Levels")
    price          = db.Column(db.Numeric(8, 2), nullable=False, default=0)
    original_price = db.Column(db.Numeric(8, 2), nullable=True)
    total_lessons  = db.Column(db.Integer, default=0)
    total_hours    = db.Column(db.Float, default=0)
    rating         = db.Column(db.Float, default=0)
    review_count   = db.Column(db.Integer, default=0)
    is_published   = db.Column(db.Boolean, default=True)
    created_at     = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    enrollments  = db.relationship("Enrollment", back_populates="course", lazy="dynamic")
    certificates = db.relationship("Certificate", back_populates="course", lazy="dynamic")

    def to_dict(self):
        return {
            "id":             self.id,
            "title":          self.title,
            "slug":           self.slug,
            "description":    self.description,
            "instructor":     self.instructor,
            "category":       self.category,
            "tag":            self.tag,
            "emoji":          self.emoji,
            "level":          self.level,
            "price":          float(self.price),
            "original_price": float(self.original_price) if self.original_price else None,
            "total_lessons":  self.total_lessons,
            "total_hours":    self.total_hours,
            "rating":         self.rating,
            "review_count":   self.review_count,
        }

class Enrollment(db.Model):
    __tablename__ = "enrollments"
    __table_args__ = (db.UniqueConstraint("user_id", "course_id", name="uq_user_course"),)
    id                  = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id             = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id           = db.Column(db.Integer, db.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    lessons_completed   = db.Column(db.Integer, default=0)
    progress_percent    = db.Column(db.Float, default=0.0)
    last_lesson_index   = db.Column(db.Integer, default=0)
    time_spent_minutes  = db.Column(db.Integer, default=0)
    enrolled_at         = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_accessed_at    = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at        = db.Column(db.DateTime, nullable=True)

    user   = db.relationship("User", back_populates="enrollments")
    course = db.relationship("Course", back_populates="enrollments")

    def to_dict(self):
        return {
            "id":                self.id,
            "course":            self.course.to_dict() if self.course else None,
            "lessons_completed": self.lessons_completed,
            "progress_percent":  self.progress_percent,
            "time_spent_minutes":self.time_spent_minutes,
            "enrolled_at":       self.enrolled_at.isoformat() if self.enrolled_at else None,
            "completed_at":      self.completed_at.isoformat() if self.completed_at else None,
        }

class Certificate(db.Model):
    __tablename__ = "certificates"
    id               = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id          = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id        = db.Column(db.Integer, db.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    certificate_code = db.Column(db.String(64), unique=True, nullable=False)
    issued_at        = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user   = db.relationship("User", back_populates="certificates")
    course = db.relationship("Course", back_populates="certificates")

    def to_dict(self):
        return {
            "id":               self.id,
            "course_title":     self.course.title if self.course else None,
            "certificate_code": self.certificate_code,
            "issued_at":        self.issued_at.isoformat() if self.issued_at else None,
        }

class ContactMessage(db.Model):
    __tablename__ = "contact_messages"
    id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name  = db.Column(db.String(80), nullable=False)
    email      = db.Column(db.String(255), nullable=False)
    company    = db.Column(db.String(120), nullable=True)
    topic      = db.Column(db.String(60), nullable=False, default="General")
    message    = db.Column(db.Text, nullable=False)
    is_read    = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", back_populates="contact_msgs")

    def to_dict(self):
        return {
            "id":         self.id,
            "first_name": self.first_name,
            "email":      self.email,
            "topic":      self.topic,
            "message":    self.message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
    