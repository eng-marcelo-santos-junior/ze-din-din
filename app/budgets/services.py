from sqlalchemy import func
from sqlalchemy.orm import joinedload

from app.extensions import db
from app.models.budget import Budget
from app.models.transaction import Transaction, TransactionType, TransactionStatus
from app.utils.money import parse_money_to_cents


def get_budgets(family_id: int, month: int, year: int) -> list[Budget]:
    return db.session.scalars(
        db.select(Budget)
        .options(joinedload(Budget.category))
        .where(Budget.family_id == family_id, Budget.month == month, Budget.year == year)
        .order_by(Budget.id)
    ).all()


def get_budget(budget_id: int, family_id: int) -> Budget | None:
    return db.session.scalar(
        db.select(Budget).where(
            Budget.id == budget_id,
            Budget.family_id == family_id,
        )
    )


def _realized_cents(family_id: int, category_id: int, month: int, year: int) -> int:
    result = db.session.scalar(
        db.select(func.coalesce(func.sum(Transaction.amount_cents), 0)).where(
            Transaction.family_id == family_id,
            Transaction.category_id == category_id,
            Transaction.type == TransactionType.EXPENSE,
            Transaction.status != TransactionStatus.CANCELED,
            func.extract('month', Transaction.transaction_date) == month,
            func.extract('year', Transaction.transaction_date) == year,
        )
    ) or 0
    return abs(result)


def get_budget_overview(family_id: int, month: int, year: int) -> list[dict]:
    budgets = get_budgets(family_id, month, year)
    overview = []
    for b in budgets:
        realized = _realized_cents(family_id, b.category_id, month, year)
        pct = round(realized / b.planned_amount_cents * 100) if b.planned_amount_cents > 0 else 0
        if pct >= 100:
            health = 'exceeded'
        elif pct >= 80:
            health = 'warning'
        else:
            health = 'healthy'
        overview.append({
            'budget': b,
            'realized_cents': realized,
            'pct': min(pct, 999),
            'health': health,
        })
    return overview


def create_budget(
    family_id: int,
    category_id: int,
    month: int,
    year: int,
    planned_amount_str: str,
) -> Budget:
    existing = db.session.scalar(
        db.select(Budget).where(
            Budget.family_id == family_id,
            Budget.category_id == category_id,
            Budget.month == month,
            Budget.year == year,
        )
    )
    if existing:
        existing.planned_amount_cents = parse_money_to_cents(planned_amount_str)
        db.session.commit()
        return existing

    budget = Budget(
        family_id=family_id,
        category_id=category_id,
        month=month,
        year=year,
        planned_amount_cents=parse_money_to_cents(planned_amount_str),
    )
    db.session.add(budget)
    db.session.commit()
    return budget


def update_budget(budget: Budget, planned_amount_str: str) -> Budget:
    budget.planned_amount_cents = parse_money_to_cents(planned_amount_str)
    db.session.commit()
    return budget


def delete_budget(budget: Budget) -> None:
    db.session.delete(budget)
    db.session.commit()


def copy_previous_month_budget(family_id: int, month: int, year: int) -> int:
    prev_month = month - 1
    prev_year = year
    if prev_month == 0:
        prev_month = 12
        prev_year -= 1

    prev_budgets = get_budgets(family_id, prev_month, prev_year)
    copied = 0
    for b in prev_budgets:
        existing = db.session.scalar(
            db.select(Budget).where(
                Budget.family_id == family_id,
                Budget.category_id == b.category_id,
                Budget.month == month,
                Budget.year == year,
            )
        )
        if not existing:
            db.session.add(Budget(
                family_id=family_id,
                category_id=b.category_id,
                month=month,
                year=year,
                planned_amount_cents=b.planned_amount_cents,
            ))
            copied += 1
    db.session.commit()
    return copied
