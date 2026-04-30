import uuid
from dataclasses import dataclass, field
from datetime import date as date_type
from typing import Optional as Opt

from app.extensions import db
from app.models.transaction import Transaction, TransactionType, TransactionStatus
from app.models.account import Account
from app.utils.money import parse_money_to_cents


# ── Filtros ────────────────────────────────────────────────────────────────────

@dataclass
class TransactionFilters:
    start_date: date_type | None = None
    end_date: date_type | None = None
    type: str | None = None
    account_id: int | None = None
    category_id: int | None = None
    status: str | None = None
    search: str | None = None


# ── Helpers de saldo ──────────────────────────────────────────────────────────

def _affects_balance(tx: Transaction) -> bool:
    return tx.status != TransactionStatus.CANCELED


def _apply_to_balance(tx: Transaction) -> None:
    """amount_cents is signed: positive = credit, negative = debit."""
    if not _affects_balance(tx):
        return
    account = db.session.get(Account, tx.account_id)
    if account:
        account.current_balance_cents += tx.amount_cents


def _reverse_from_balance(tx: Transaction) -> None:
    if not _affects_balance(tx):
        return
    account = db.session.get(Account, tx.account_id)
    if account:
        account.current_balance_cents -= tx.amount_cents


def _signed_amount(amount_str: str, tx_type: str) -> int:
    """Convert form money string to signed integer cents based on type."""
    cents = parse_money_to_cents(amount_str)
    if tx_type in (TransactionType.EXPENSE,):
        return -abs(cents)
    return abs(cents)


# ── CRUD ──────────────────────────────────────────────────────────────────────

def get_transactions(
    family_id: int,
    filters: TransactionFilters | None = None,
    page: int = 1,
    per_page: int = 20,
):
    q = (
        db.select(Transaction)
        .where(Transaction.family_id == family_id)
        .order_by(Transaction.transaction_date.desc(), Transaction.id.desc())
    )
    if filters:
        if filters.start_date:
            q = q.where(Transaction.transaction_date >= filters.start_date)
        if filters.end_date:
            q = q.where(Transaction.transaction_date <= filters.end_date)
        if filters.type:
            q = q.where(Transaction.type == filters.type)
        if filters.account_id:
            q = q.where(Transaction.account_id == filters.account_id)
        if filters.category_id:
            q = q.where(Transaction.category_id == filters.category_id)
        if filters.status:
            q = q.where(Transaction.status == filters.status)
        if filters.search:
            q = q.where(Transaction.description.ilike(f'%{filters.search}%'))
    return db.paginate(q, page=page, per_page=per_page, error_out=False)


def get_transaction(tx_id: int, family_id: int) -> Transaction | None:
    return db.session.scalar(
        db.select(Transaction).where(
            Transaction.id == tx_id,
            Transaction.family_id == family_id,
        )
    )


def create_transaction(
    family_id: int,
    user_id: int,
    account_id: int,
    tx_type: str,
    description: str,
    amount_str: str,
    transaction_date: date_type,
    category_id: int | None = None,
    competence_date: date_type | None = None,
    status: str = TransactionStatus.PAID,
    payment_method: str | None = None,
    notes: str | None = None,
) -> Transaction:
    amount_cents = _signed_amount(amount_str, tx_type)
    tx = Transaction(
        family_id=family_id,
        user_id=user_id,
        account_id=account_id,
        category_id=category_id or None,
        type=tx_type,
        description=description.strip(),
        amount_cents=amount_cents,
        transaction_date=transaction_date,
        competence_date=competence_date or transaction_date,
        status=status,
        payment_method=payment_method or None,
        notes=notes.strip() if notes else None,
    )
    db.session.add(tx)
    db.session.flush()
    _apply_to_balance(tx)
    db.session.commit()
    return tx


def update_transaction(
    tx: Transaction,
    account_id: int,
    tx_type: str,
    description: str,
    amount_str: str,
    transaction_date: date_type,
    category_id: int | None = None,
    competence_date: date_type | None = None,
    status: str = TransactionStatus.PAID,
    payment_method: str | None = None,
    notes: str | None = None,
) -> Transaction:
    _reverse_from_balance(tx)

    tx.account_id = account_id
    tx.type = tx_type
    tx.description = description.strip()
    tx.amount_cents = _signed_amount(amount_str, tx_type)
    tx.transaction_date = transaction_date
    tx.competence_date = competence_date or transaction_date
    tx.category_id = category_id or None
    tx.status = status
    tx.payment_method = payment_method or None
    tx.notes = notes.strip() if notes else None

    _apply_to_balance(tx)
    db.session.commit()
    return tx


def delete_transaction(tx: Transaction) -> None:
    _reverse_from_balance(tx)
    db.session.delete(tx)
    db.session.commit()


def duplicate_transaction(tx: Transaction, new_date: date_type) -> Transaction:
    copy = Transaction(
        family_id=tx.family_id,
        user_id=tx.user_id,
        account_id=tx.account_id,
        category_id=tx.category_id,
        type=tx.type,
        description=tx.description,
        amount_cents=tx.amount_cents,
        transaction_date=new_date,
        competence_date=new_date,
        status=TransactionStatus.PENDING,
        payment_method=tx.payment_method,
        notes=tx.notes,
    )
    db.session.add(copy)
    db.session.flush()
    _apply_to_balance(copy)
    db.session.commit()
    return copy


def mark_as_paid(tx: Transaction) -> Transaction:
    if tx.status == TransactionStatus.PENDING:
        new_status = (
            TransactionStatus.RECEIVED
            if tx.type in (TransactionType.INCOME, TransactionType.REFUND)
            else TransactionStatus.PAID
        )
        tx.status = new_status
        db.session.commit()
    return tx


# ── Transferência ─────────────────────────────────────────────────────────────

def create_transfer(
    family_id: int,
    user_id: int,
    from_account_id: int,
    to_account_id: int,
    amount_str: str,
    description: str,
    transaction_date: date_type,
    notes: str | None = None,
) -> tuple[Transaction, Transaction]:
    group_id = str(uuid.uuid4())
    amount_cents = abs(parse_money_to_cents(amount_str))

    out_tx = Transaction(
        family_id=family_id,
        user_id=user_id,
        account_id=from_account_id,
        type=TransactionType.TRANSFER,
        description=description.strip(),
        amount_cents=-amount_cents,
        transaction_date=transaction_date,
        competence_date=transaction_date,
        status=TransactionStatus.PAID,
        transfer_group_id=group_id,
        notes=notes.strip() if notes else None,
    )
    in_tx = Transaction(
        family_id=family_id,
        user_id=user_id,
        account_id=to_account_id,
        type=TransactionType.TRANSFER,
        description=description.strip(),
        amount_cents=amount_cents,
        transaction_date=transaction_date,
        competence_date=transaction_date,
        status=TransactionStatus.RECEIVED,
        transfer_group_id=group_id,
        notes=notes.strip() if notes else None,
    )
    db.session.add_all([out_tx, in_tx])
    db.session.flush()
    _apply_to_balance(out_tx)
    _apply_to_balance(in_tx)
    db.session.commit()
    return out_tx, in_tx


# ── Resumo financeiro ─────────────────────────────────────────────────────────

def get_period_summary(family_id: int, filters: TransactionFilters) -> dict:
    """Returns total income_cents, expense_cents and balance for the filtered period."""
    q = db.select(Transaction).where(
        Transaction.family_id == family_id,
        Transaction.status != TransactionStatus.CANCELED,
        Transaction.type.notin_([TransactionType.TRANSFER]),
    )
    if filters.start_date:
        q = q.where(Transaction.transaction_date >= filters.start_date)
    if filters.end_date:
        q = q.where(Transaction.transaction_date <= filters.end_date)
    if filters.account_id:
        q = q.where(Transaction.account_id == filters.account_id)

    txs = db.session.scalars(q).all()
    income = sum(tx.amount_cents for tx in txs if tx.amount_cents > 0)
    expense = sum(abs(tx.amount_cents) for tx in txs if tx.amount_cents < 0)
    return {
        'income_cents': income,
        'expense_cents': expense,
        'result_cents': income - expense,
    }
