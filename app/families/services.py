from app.extensions import db
from app.models.family import Family, FamilyMember, FamilyRole, FamilyMemberStatus


def create_family(name: str, currency: str, owner_user_id: int) -> Family:
    from app.categories.services import seed_default_categories

    family = Family(name=name.strip(), currency=currency, created_by=owner_user_id)
    db.session.add(family)
    db.session.flush()

    owner = FamilyMember(
        family_id=family.id,
        user_id=owner_user_id,
        role=FamilyRole.OWNER,
        status=FamilyMemberStatus.ACTIVE,
    )
    db.session.add(owner)
    seed_default_categories(family.id)
    db.session.commit()
    return family


def get_members(family_id: int) -> list[FamilyMember]:
    return db.session.scalars(
        db.select(FamilyMember)
        .where(
            FamilyMember.family_id == family_id,
            FamilyMember.status != FamilyMemberStatus.REMOVED,
        )
        .order_by(FamilyMember.created_at)
    ).all()


def update_family(family: Family, name: str, currency: str) -> Family:
    family.name = name.strip()
    family.currency = currency
    db.session.commit()
    return family


def get_user_membership(user_id: int, family_id: int) -> FamilyMember | None:
    return db.session.scalar(
        db.select(FamilyMember).where(
            FamilyMember.user_id == user_id,
            FamilyMember.family_id == family_id,
            FamilyMember.status == FamilyMemberStatus.ACTIVE,
        )
    )
