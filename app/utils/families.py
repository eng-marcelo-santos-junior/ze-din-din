from app.extensions import db
from app.models.family import Family, FamilyMember, FamilyMemberStatus


def get_current_family(user) -> Family | None:
    if not user or not user.is_authenticated:
        return None
    membership = db.session.scalar(
        db.select(FamilyMember)
        .where(
            FamilyMember.user_id == user.id,
            FamilyMember.status == FamilyMemberStatus.ACTIVE,
        )
        .order_by(FamilyMember.created_at)
    )
    return membership.family if membership else None


def user_has_access_to_family(user_id: int, family_id: int) -> bool:
    membership = db.session.scalar(
        db.select(FamilyMember).where(
            FamilyMember.user_id == user_id,
            FamilyMember.family_id == family_id,
            FamilyMember.status == FamilyMemberStatus.ACTIVE,
        )
    )
    return membership is not None
