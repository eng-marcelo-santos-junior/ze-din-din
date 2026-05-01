from datetime import date
from sqlalchemy import func
from sqlalchemy.orm import joinedload

from app.extensions import db
from app.models.transaction import Transaction, TransactionType, TransactionStatus
from app.models.account import Account
from app.models.category import Category
from app.models.user import User

PT_MONTHS = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
             'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']


def _prev_month(year: int, month: int, n: int) -> tuple[int, int]:
    total = year * 12 + month - 1 - n
    return total // 12, total % 12 + 1


def get_monthly_cash_flow(family_id: int, num_months: int = 12) -> list[dict]:
    today = date.today()
    results = []
    for i in range(num_months - 1, -1, -1):
        y, m = _prev_month(today.year, today.month, i)
        income = db.session.scalar(
            db.select(func.coalesce(func.sum(Transaction.amount_cents), 0)).where(
                Transaction.family_id == family_id,
                Transaction.status != TransactionStatus.CANCELED,
                Transaction.type == TransactionType.INCOME,
                func.extract('month', Transaction.transaction_date) == m,
                func.extract('year', Transaction.transaction_date) == y,
            )
        ) or 0
        expenses = abs(db.session.scalar(
            db.select(func.coalesce(func.sum(Transaction.amount_cents), 0)).where(
                Transaction.family_id == family_id,
                Transaction.status != TransactionStatus.CANCELED,
                Transaction.type == TransactionType.EXPENSE,
                func.extract('month', Transaction.transaction_date) == m,
                func.extract('year', Transaction.transaction_date) == y,
            )
        ) or 0)
        results.append({
            'label': f"{PT_MONTHS[m - 1]}/{str(y)[2:]}",
            'year': y,
            'month': m,
            'income_cents': income,
            'expense_cents': expenses,
            'result_cents': income - expenses,
        })
    return results


def get_expenses_by_category(
    family_id: int,
    start_date: date | None = None,
    end_date: date | None = None,
    account_id: int | None = None,
) -> list[dict]:
    q = (
        db.select(
            func.coalesce(Category.name, 'Sem categoria').label('name'),
            func.coalesce(Category.color, '#6c757d').label('color'),
            func.sum(Transaction.amount_cents).label('total'),
        )
        .select_from(Transaction)
        .outerjoin(Category, Transaction.category_id == Category.id)
        .where(
            Transaction.family_id == family_id,
            Transaction.status != TransactionStatus.CANCELED,
            Transaction.type == TransactionType.EXPENSE,
        )
        .group_by(Transaction.category_id, Category.name, Category.color)
        .order_by(func.sum(Transaction.amount_cents))
    )
    if start_date:
        q = q.where(Transaction.transaction_date >= start_date)
    if end_date:
        q = q.where(Transaction.transaction_date <= end_date)
    if account_id:
        q = q.where(Transaction.account_id == account_id)

    rows = db.session.execute(q).all()
    total = sum(abs(r.total) for r in rows)
    return [
        {
            'name': r.name,
            'color': r.color,
            'total_cents': abs(r.total),
            'pct': round(abs(r.total) / total * 100) if total else 0,
        }
        for r in rows
    ]


def get_expenses_by_member(
    family_id: int,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[dict]:
    q = (
        db.select(
            User.name.label('name'),
            func.sum(Transaction.amount_cents).label('total'),
        )
        .select_from(Transaction)
        .join(User, Transaction.user_id == User.id)
        .where(
            Transaction.family_id == family_id,
            Transaction.status != TransactionStatus.CANCELED,
            Transaction.type == TransactionType.EXPENSE,
        )
        .group_by(User.id, User.name)
        .order_by(func.sum(Transaction.amount_cents))
    )
    if start_date:
        q = q.where(Transaction.transaction_date >= start_date)
    if end_date:
        q = q.where(Transaction.transaction_date <= end_date)

    rows = db.session.execute(q).all()
    total = sum(abs(r.total) for r in rows)
    return [
        {
            'name': r.name,
            'total_cents': abs(r.total),
            'pct': round(abs(r.total) / total * 100) if total else 0,
        }
        for r in rows
    ]


def get_budget_vs_actual(family_id: int, month: int, year: int) -> list[dict]:
    from app.budgets.services import get_budget_overview
    return get_budget_overview(family_id, month, year)


def get_biggest_expenses(
    family_id: int,
    start_date: date | None = None,
    end_date: date | None = None,
    account_id: int | None = None,
    limit: int = 20,
) -> list[Transaction]:
    q = (
        db.select(Transaction)
        .options(
            joinedload(Transaction.account),
            joinedload(Transaction.category),
            joinedload(Transaction.user),
        )
        .where(
            Transaction.family_id == family_id,
            Transaction.status != TransactionStatus.CANCELED,
            Transaction.type == TransactionType.EXPENSE,
        )
        .order_by(Transaction.amount_cents)
        .limit(limit)
    )
    if start_date:
        q = q.where(Transaction.transaction_date >= start_date)
    if end_date:
        q = q.where(Transaction.transaction_date <= end_date)
    if account_id:
        q = q.where(Transaction.account_id == account_id)

    return db.session.scalars(q).all()


def get_net_worth_summary(family_id: int) -> dict:
    accounts = db.session.scalars(
        db.select(Account)
        .where(Account.family_id == family_id, Account.is_active == True)  # noqa: E712
        .order_by(Account.name)
    ).all()

    total_assets = sum(a.current_balance_cents for a in accounts if a.current_balance_cents > 0)
    total_liabilities = sum(
        abs(a.current_balance_cents) for a in accounts if a.current_balance_cents < 0
    )
    net_worth = sum(a.current_balance_cents for a in accounts)

    return {
        'accounts': accounts,
        'total_assets': total_assets,
        'total_liabilities': total_liabilities,
        'net_worth': net_worth,
    }


def get_recurring_expenses(
    family_id: int,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[Transaction]:
    q = (
        db.select(Transaction)
        .options(joinedload(Transaction.account), joinedload(Transaction.category))
        .where(
            Transaction.family_id == family_id,
            Transaction.status != TransactionStatus.CANCELED,
            Transaction.type == TransactionType.EXPENSE,
            Transaction.recurring_rule_id.isnot(None),
        )
        .order_by(Transaction.transaction_date.desc())
    )
    if start_date:
        q = q.where(Transaction.transaction_date >= start_date)
    if end_date:
        q = q.where(Transaction.transaction_date <= end_date)
    return db.session.scalars(q).all()
