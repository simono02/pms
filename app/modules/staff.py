import json
import secrets
from datetime import datetime, timedelta

from flask import current_app
from flask_mail import Message
from app import db, mail
from app.models.staff import Staff
from app.models.user import User
from app.models.project import Project
from app.modules.user import UserModule


class StaffModule:
    """Business logic for Staff operations — email delivery included."""

    # ==================================================================
    # EMAIL  (private helper)
    # ==================================================================

    @staticmethod
    def _send_verification_email(email: str, name: str, token: str):
        frontend_url  = current_app.config.get('FRONTEND_URL', 'http://localhost:3000')
        support_email = current_app.config.get('MAIL_DEFAULT_SENDER', '')
        app_name      = current_app.config.get('APP_NAME', 'ResearchPro')
        setup_link    = f"{frontend_url}/staff/setup-password?token={token}"
        subject       = f"Welcome to {app_name} – Set Up Your Account"

        html_body = f"""
        <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;">
            <div style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);
                        padding:30px;border-radius:12px 12px 0 0;text-align:center;">
                <h1 style="color:white;margin:0;font-size:26px;">Welcome to {app_name}</h1>
            </div>
            <div style="background:#fff;padding:30px;border:1px solid #e1e8ed;
                        border-radius:0 0 12px 12px;">
                <p style="font-size:16px;color:#2c3e50;">Hello <strong>{name}</strong>,</p>
                <p style="color:#555;line-height:1.6;">
                    You have been added as a <strong>Staff Member</strong> on {app_name}.
                    Click the button below to verify your email and create your password.
                </p>
                <p style="color:#e74c3c;font-size:14px;">
                    &#9888;&#65039; This link is valid for <strong>48 hours</strong> only.
                </p>
                <div style="text-align:center;margin:32px 0;">
                    <a href="{setup_link}"
                       style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);
                              color:white;padding:14px 36px;border-radius:8px;
                              text-decoration:none;font-size:16px;font-weight:600;
                              display:inline-block;">
                        Verify Email &amp; Set Password
                    </a>
                </div>
                <p style="color:#888;font-size:13px;">
                    Or copy this link:<br/>
                    <a href="{setup_link}" style="color:#667eea;word-break:break-all;">
                        {setup_link}
                    </a>
                </p>
                <hr style="border:none;border-top:1px solid #e1e8ed;margin:24px 0;"/>
                <p style="color:#aaa;font-size:12px;text-align:center;">
                    Not expecting this? Contact
                    <a href="mailto:{support_email}" style="color:#667eea;">{support_email}</a>.
                </p>
            </div>
        </div>"""

        text_body = (
            f"Hello {name},\n\n"
            f"You have been added as a Staff Member on {app_name}.\n"
            f"Set up your account here:\n\n{setup_link}\n\n"
            f"Link expires in 48 hours.\n\n"
            f"Not expecting this? Contact {support_email}."
        )

        mail.send(Message(subject=subject, recipients=[email],
                          body=text_body, html=html_body))

    # ==================================================================
    # SERIALISATION
    # ==================================================================

    @staticmethod
    def to_dict(staff):
        return {
            'id':                      staff.id,
            'user_id':                 staff.user_id,
            'id_number':               staff.id_number,
            'specialization':          staff.specialization,
            'experience_years':        staff.experience_years,
            'qualification':           staff.qualification,
            'bio':                     staff.bio,
            'rate_per_page':           staff.rate_per_page,
            'rate_per_chapter':        staff.rate_per_chapter,
            'availability':            staff.availability,
            'rating':                  staff.rating,
            'total_projects':          staff.total_projects,
            'completed_projects':      staff.completed_projects,
            'skills':                  StaffModule.get_skills_list(staff),
            'password_set':            staff.password_set,
            'created_at':              staff.created_at.isoformat() if staff.created_at else None,
            'updated_at':              staff.updated_at.isoformat() if staff.updated_at else None,
            'assigned_projects_count': staff.assigned_projects.count(),
            # Nested user block — matches what StaffView.jsx expects
            'user': {
                'id':    staff.user.id,
                'name':  staff.user.name,
                'email': staff.user.email,
                'phone': staff.user.phone,
            } if staff.user else None,
        }

    # ==================================================================
    # SKILLS
    # ==================================================================

    @staticmethod
    def get_skills_list(staff):
        if not staff.skills:
            return []
        try:
            return json.loads(staff.skills)
        except Exception:
            return []

    @staticmethod
    def set_skills_list(staff, skills_list):
        staff.skills = json.dumps(skills_list)
        db.session.commit()

    # ==================================================================
    # STAFF CREATION
    # ==================================================================

    @staticmethod
    def create_staff(
        name: str,
        email: str,
        id_number: str,
        specialization: str = None,
        experience_years: int = 0,
        qualification: str = None,
        bio: str = None,
        rate_per_page: float = None,
        rate_per_chapter: float = None,
        skills: list = None,
        phone: str = None,
    ):
        email     = email.strip().lower()
        id_number = id_number.strip()

        if User.query.filter_by(email=email).first():
            raise ValueError('A user with this email already exists.')
        if Staff.query.filter_by(id_number=id_number).first():
            raise ValueError('A staff member with this ID number already exists.')

        # Temporary password — replaced when staff completes setup
        temp_password = secrets.token_urlsafe(32)

        user = User(
            name=name.strip(),
            email=email,
            role='staff',
            status='active',
            phone=phone,
            email_verified=False,
        )
        UserModule.set_password(user, temp_password)
        db.session.add(user)
        db.session.flush()  # get user.id before creating Staff row

        token = secrets.token_urlsafe(48)
        staff = Staff(
            user_id=user.id,
            id_number=id_number,
            specialization=specialization,
            experience_years=experience_years or 0,
            qualification=qualification,
            bio=bio,
            rate_per_page=rate_per_page,
            rate_per_chapter=rate_per_chapter,
            skills=json.dumps(skills) if skills else '[]',
            availability=True,
            password_set=False,
            verification_token=token,
            verification_token_expires=datetime.utcnow() + timedelta(hours=48),
        )
        db.session.add(staff)
        db.session.commit()

        try:
            StaffModule._send_verification_email(email=email, name=name.strip(), token=token)
        except Exception as e:
            current_app.logger.error(f"[StaffModule] Email failed for {email}: {e}")

        return staff

    # ==================================================================
    # RESEND VERIFICATION
    # ==================================================================

    @staticmethod
    def resend_verification_email(staff):
        if staff.password_set:
            raise ValueError('This staff member has already set their password.')
        token = secrets.token_urlsafe(48)
        staff.verification_token         = token
        staff.verification_token_expires = datetime.utcnow() + timedelta(hours=48)
        db.session.commit()
        StaffModule._send_verification_email(
            email=staff.user.email, name=staff.user.name, token=token)
        return staff

    # ==================================================================
    # VERIFY TOKEN + SET PASSWORD
    # ==================================================================

    @staticmethod
    def verify_and_set_password(token: str, new_password: str):
        staff = Staff.query.filter_by(verification_token=token).first()
        if not staff:
            raise ValueError('Invalid verification token.')
        if not staff.verification_token_expires or \
                datetime.utcnow() > staff.verification_token_expires:
            raise ValueError('Token has expired. Ask an admin to resend your invite.')
        if len(new_password) < 8:
            raise ValueError('Password must be at least 8 characters.')

        UserModule.set_password(staff.user, new_password)
        staff.user.email_verified        = True
        staff.verification_token         = None
        staff.verification_token_expires = None
        staff.password_set               = True
        staff.updated_at                 = datetime.utcnow()
        db.session.commit()
        return staff

    # ==================================================================
    # LOOKUP HELPERS
    # ==================================================================

    @staticmethod
    def find_by_id(staff_id):
        return db.session.get(Staff, staff_id)

    @staticmethod
    def find_by_user_id(user_id):
        return Staff.query.filter_by(user_id=user_id).first()

    @staticmethod
    def find_by_token(token: str):
        return Staff.query.filter_by(verification_token=token).first()

    @staticmethod
    def get_available_staff():
        return Staff.query.filter_by(availability=True).all()

    @staticmethod
    def get_staff_by_specialization(specialization):
        return Staff.query.filter_by(specialization=specialization, availability=True).all()

    @staticmethod
    def get_top_rated_staff(limit=10):
        return (Staff.query
                .filter_by(availability=True)
                .order_by(Staff.rating.desc())
                .limit(limit).all())

    # ==================================================================
    # PROFILE UPDATE
    # ==================================================================

    @staticmethod
    def update_profile(staff, **kwargs):
        allowed_fields = [
            'specialization', 'experience_years', 'qualification',
            'bio', 'availability', 'rate_per_page', 'rate_per_chapter',
        ]
        for field in allowed_fields:
            if field in kwargs:
                setattr(staff, field, kwargs[field])
        if 'skills' in kwargs:
            staff.skills = json.dumps(
                kwargs['skills'] if isinstance(kwargs['skills'], list) else []
            )
        staff.updated_at = datetime.utcnow()
        db.session.commit()
        return staff

    @staticmethod
    def set_availability(staff, available: bool):
        staff.availability = available
        staff.updated_at   = datetime.utcnow()
        db.session.commit()

    # ==================================================================
    # PROJECT HELPERS
    # ==================================================================

    @staticmethod
    def get_assigned_projects(staff):
        return staff.assigned_projects.all()

    @staticmethod
    def get_active_projects(staff):
        return staff.assigned_projects.filter(
            Project.status.in_(['pending', 'in_progress'])
        ).all()

    @staticmethod
    def get_completed_projects(staff):
        return staff.assigned_projects.filter_by(status='completed').all()

    @staticmethod
    def can_take_project(staff):
        if not staff.availability:
            return False
        return len(StaffModule.get_active_projects(staff)) < 5

    @staticmethod
    def assign_project(staff, project):
        if not StaffModule.can_take_project(staff):
            raise ValueError('Staff member cannot take more projects.')
        project.assigned_staff_id = staff.id
        project.status            = 'in_progress'
        staff.total_projects      = (staff.total_projects or 0) + 1
        db.session.commit()

    @staticmethod
    def complete_project(staff, project):
        if project.assigned_staff_id != staff.id:
            raise ValueError('Project not assigned to this staff member.')
        project.status           = 'payment_required'
        staff.completed_projects = (staff.completed_projects or 0) + 1
        StaffModule._update_rating(staff)
        db.session.commit()

    # ==================================================================
    # RATING  (private — called automatically on project completion)
    # ==================================================================

    @staticmethod
    def _update_rating(staff):
        if not staff.completed_projects:
            staff.rating = 0.0
            return
        base            = 4.0
        exp_bonus       = min((staff.experience_years or 0) * 0.1, 1.0)
        completion_rate = staff.completed_projects / max(staff.total_projects or 1, 1)
        staff.rating    = round(min(base + exp_bonus + completion_rate, 5.0), 2)

    # ==================================================================
    # STATS
    # ==================================================================

    @staticmethod
    def get_performance_stats(staff):
        total           = staff.total_projects or 0
        completed       = staff.completed_projects or 0
        completion_rate = (completed / max(total, 1)) * 100
        return {
            'total_projects':     total,
            'completed_projects': completed,
            'completion_rate':    round(completion_rate, 2),
            'rating':             round(staff.rating or 0, 2),
            'active_projects':    len(StaffModule.get_active_projects(staff)),
            'available_slots':    5 - len(StaffModule.get_active_projects(staff)),
            'can_take_more':      StaffModule.can_take_project(staff),
        }

    # ==================================================================
    # DELETE
    # ==================================================================

    @staticmethod
    def delete(staff):
        user = staff.user
        db.session.delete(staff)
        if user:
            db.session.delete(user)
        db.session.commit()