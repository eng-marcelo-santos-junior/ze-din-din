from flask import abort
from app.extensions import db
from app.models.family import FamilyMember, FamilyMemberStatus


def user_has_access_to_family(user_id: int, family_id: int) -> bool:
    """True se o usuário é membro ativo da família."""
    return db.session.scalar(
        db.select(FamilyMember).where(
            FamilyMember.user_id == user_id,
            FamilyMember.family_id == family_id,
            FamilyMember.status == FamilyMemberStatus.ACTIVE,
        )
    ) is not None


def assert_family_access(user_id: int, family_id: int) -> None:
    """Levanta 403 se o usuário não pertence à família."""
    if not user_has_access_to_family(user_id, family_id):
        abort(403)
