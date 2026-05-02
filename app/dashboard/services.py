from dataclasses import dataclass
from datetime import date
from sqlalchemy import func, asc
from sqlalchemy.orm import joinedload
from ..extensions import db
from ..models.transaction import Transaction, TransactionType, TransactionStatus
from ..models.account import Account
from ..models.category import Category


PT_MONTHS = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
             'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']


@dataclass
class DashboardFilters:
    month: int = None
    year: int = None
    account_id: int | None = None

    def __post_init__(self):
        today = date.today()
        if self.month is None:
            self.month = today.month
        if self.year is None:
            self.year = today.year


def _prev_month(year: int, month: int, n: int) -> tuple[int, int]:
    total = year * 12 + month - 1 - n
    return total // 12, total % 12 + 1


def get_total_balance(family_id: int) -> int:
    return db.session.scalar(
        db.select(func.coalesce(func.sum(Account.current_balance_cents), 0))
        .where(Account.family_id == family_id, Account.is_active == True)  # noqa: E712
    ) or 0


def get_month_income(family_id: int, filters: DashboardFilters) -> int:
    q = db.select(func.coalesce(func.sum(Transaction.amount_cents), 0)).where(
        Transaction.family_id == family_id,
        Transaction.status != TransactionStatus.CANCELED,
        Transaction.type == TransactionType.INCOME,
        func.extract('month', Transaction.transaction_date) == filters.month,
        func.extract('year', Transaction.transaction_date) == filters.year,
    )
    if filters.account_id:
        q = q.where(Transaction.account_id == filters.account_id)
    return db.session.scalar(q) or 0


def get_month_expenses(family_id: int, filters: DashboardFilters) -> int:
    q = db.select(func.coalesce(func.sum(Transaction.amount_cents), 0)).where(
        Transaction.family_id == family_id,
        Transaction.status != TransactionStatus.CANCELED,
        Transaction.type == TransactionType.EXPENSE,
        func.extract('month', Transaction.transaction_date) == filters.month,
        func.extract('year', Transaction.transaction_date) == filters.year,
    )
    if filters.account_id:
        q = q.where(Transaction.account_id == filters.account_id)
    return abs(db.session.scalar(q) or 0)


def get_month_result(family_id: int, filters: DashboardFilters) -> int:
    return get_month_income(family_id, filters) - get_month_expenses(family_id, filters)


def get_month_transaction_count(family_id: int, filters: DashboardFilters) -> int:
    q = db.select(func.count(Transaction.id)).where(
        Transaction.family_id == family_id,
        Transaction.status != TransactionStatus.CANCELED,
        Transaction.type.in_([TransactionType.INCOME, TransactionType.EXPENSE]),
        func.extract('month', Transaction.transaction_date) == filters.month,
        func.extract('year', Transaction.transaction_date) == filters.year,
    )
    if filters.account_id:
        q = q.where(Transaction.account_id == filters.account_id)
    return db.session.scalar(q) or 0


def get_expenses_by_category(family_id: int, filters: DashboardFilters) -> list[dict]:
    q = (
        db.select(
            func.coalesce(Category.name, 'Sem categoria').label('name'),
            func.sum(Transaction.amount_cents).label('total'),
        )
        .select_from(Transaction)
        .outerjoin(Category, Transaction.category_id == Category.id)
        .where(
            Transaction.family_id == family_id,
            Transaction.status != TransactionStatus.CANCELED,
            Transaction.type == TransactionType.EXPENSE,
            func.extract('month', Transaction.transaction_date) == filters.month,
            func.extract('year', Transaction.transaction_date) == filters.year,
        )
        .group_by(Transaction.category_id, Category.name)
        .order_by(asc(func.sum(Transaction.amount_cents)))
    )
    if filters.account_id:
        q = q.where(Transaction.account_id == filters.account_id)
    rows = db.session.execute(q).all()
    return [{'name': r.name, 'total_cents': abs(r.total)} for r in rows]


def get_income_vs_expense_by_month(family_id: int, num_months: int = 6) -> list[dict]:
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
            'income_cents': income,
            'expense_cents': expenses,
        })
    return results


def get_recent_transactions(family_id: int, limit: int = 10):
    return db.session.scalars(
        db.select(Transaction)
        .options(joinedload(Transaction.account), joinedload(Transaction.category))
        .where(
            Transaction.family_id == family_id,
            Transaction.status != TransactionStatus.CANCELED,
        )
        .order_by(Transaction.transaction_date.desc(), Transaction.created_at.desc())
        .limit(limit)
    ).all()


def get_top_expense_category(family_id: int, filters: DashboardFilters) -> dict | None:
    cats = get_expenses_by_category(family_id, filters)
    return cats[0] if cats else None


def get_upcoming_bills_placeholder() -> list:
    return []
