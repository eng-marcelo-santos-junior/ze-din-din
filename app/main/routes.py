from flask import render_template
from flask_login import login_required, current_user
from . import main_bp
from app.utils.families import get_current_family
from app.models.family import FamilyMember, FamilyMemberStatus
from app.extensions import db


@main_bp.route('/')
def index():
    return render_template('main/index.html')


@main_bp.route('/profile')
@login_required
def profile():
    family = get_current_family(current_user)
    membership = None
    if family:
        membership = db.session.scalar(
            db.select(FamilyMember).where(
                FamilyMember.user_id == current_user.id,
                FamilyMember.family_id == family.id,
                FamilyMember.status == FamilyMemberStatus.ACTIVE,
            )
        )
    return render_template('main/profile.html', family=family, membership=membership)
