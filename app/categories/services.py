from app.extensions import db
from app.models.category import Category, CategoryType

_DEFAULT_INCOME = [
    ('Salário', '#198754', 'bi-briefcase'),
    ('Freelance', '#0d6efd', 'bi-laptop'),
    ('Investimentos', '#0dcaf0', 'bi-graph-up-arrow'),
    ('Reembolso', '#6f42c1', 'bi-arrow-return-left'),
    ('Outros', '#6c757d', 'bi-three-dots'),
]

_DEFAULT_EXPENSE = [
    ('Alimentação', '#fd7e14', 'bi-basket'),
    ('Moradia', '#795548', 'bi-house'),
    ('Transporte', '#0d6efd', 'bi-car-front'),
    ('Saúde', '#dc3545', 'bi-heart-pulse'),
    ('Educação', '#6f42c1', 'bi-book'),
    ('Lazer', '#ffc107', 'bi-controller'),
    ('Mercado', '#198754', 'bi-cart'),
    ('Energia', '#fd7e14', 'bi-lightning-charge'),
    ('Água', '#0dcaf0', 'bi-droplet'),
    ('Internet', '#0d6efd', 'bi-wifi'),
    ('Assinaturas', '#6f42c1', 'bi-play-circle'),
    ('Impostos', '#dc3545', 'bi-receipt'),
    ('Pets', '#ffc107', 'bi-heart'),
    ('Outros', '#6c757d', 'bi-three-dots'),
]


def seed_default_categories(family_id: int) -> None:
    for name, color, icon in _DEFAULT_INCOME:
        db.session.add(Category(
            family_id=family_id,
            name=name,
            type=CategoryType.INCOME,
            color=color,
            icon=icon,
            is_default=True,
        ))
    for name, color, icon in _DEFAULT_EXPENSE:
        db.session.add(Category(
            family_id=family_id,
            name=name,
            type=CategoryType.EXPENSE,
            color=color,
            icon=icon,
            is_default=True,
        ))
    db.session.flush()


def get_categories(
    family_id: int,
    category_type: str | None = None,
    active_only: bool = True,
    parent_only: bool = False,
) -> list[Category]:
    q = db.select(Category).where(Category.family_id == family_id)
    if active_only:
        q = q.where(Category.is_active == True)
    if category_type:
        q = q.where(Category.type == category_type)
    if parent_only:
        q = q.where(Category.parent_id == None)
    q = q.order_by(Category.type, Category.name)
    return db.session.scalars(q).all()


def get_category(category_id: int, family_id: int) -> Category | None:
    return db.session.scalar(
        db.select(Category).where(
            Category.id == category_id,
            Category.family_id == family_id,
        )
    )


def create_category(
    family_id: int,
    name: str,
    category_type: str,
    color: str = '#6c757d',
    icon: str = 'bi-tag',
    parent_id: int | None = None,
) -> Category:
    category = Category(
        family_id=family_id,
        name=name.strip(),
        type=category_type,
        color=color,
        icon=icon,
        parent_id=parent_id or None,
    )
    db.session.add(category)
    db.session.commit()
    return category


def update_category(
    category: Category,
    name: str,
    category_type: str,
    color: str,
    icon: str,
    parent_id: int | None = None,
) -> Category:
    category.name = name.strip()
    category.type = category_type
    category.color = color
    category.icon = icon
    category.parent_id = parent_id or None
    db.session.commit()
    return category


def archive_category(category: Category) -> Category:
    category.is_active = False
    db.session.commit()
    return category
