from functools import wraps
from flask import redirect, url_for, flash, g
from flask_login import current_user
from .families import get_current_family
from app.models.family import FamilyRole


def family_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        family = get_current_family(current_user)
        if family is None:
            flash('Crie uma família para começar a usar o Zé Din Din.', 'warning')
            return redirect(url_for('families.new'))
        g.current_family = family
        return f(*args, **kwargs)
    return decorated


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            family = getattr(g, 'current_family', None) or get_current_family(current_user)
            if family is None:
                return redirect(url_for('families.new'))
            from app.models.family import FamilyMember, FamilyMemberStatus
            from app.extensions import db
            membership = db.session.scalar(
                db.select(FamilyMember).where(
                    FamilyMember.user_id == current_user.id,
                    FamilyMember.family_id == family.id,
                    FamilyMember.status == FamilyMemberStatus.ACTIVE,
                )
            )
            if not membership or membership.role not in [r.value if hasattr(r, 'value') else r for r in roles]:
                flash('Você não tem permissão para realizar esta ação.', 'danger')
                return redirect(url_for('dashboard.index'))
            return f(*args, **kwargs)
        return decorated
    return decorator
