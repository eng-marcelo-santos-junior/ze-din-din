from datetime import date

from app.extensions import db
from app.models.bill import Bill, BillType, BillStatus
from app.models.transaction import TransactionType, TransactionStatus
from app.utils.money import parse_money_to_cents, format_cents_to_money


def get_bills(
    family_id: int,
    bill_type: str | None = None,
    active_only: bool = False,
) -> list[Bill]:
    q = (
        db.select(Bill)
        .where(Bill.family_id == family_id)
        .order_by(Bill.due_date)
    )
    if bill_type:
        q = q.where(Bill.type == bill_type)
    if active_only:
        q = q.where(Bill.status == BillStatus.PENDING)
    return db.session.scalars(q).all()


def get_bill(bill_id: int, family_id: int) -> Bill | None:
    return db.session.scalar(
        db.select(Bill).where(
            Bill.id == bill_id,
            Bill.family_id == family_id,
        )
    )


def create_bill(
    family_id: int,
    description: str,
    bill_type: str,
    amount_str: str,
    due_date: date,
    account_id: int | None = None,
    category_id: int | None = None,
) -> Bill:
    bill = Bill(
        family_id=family_id,
        description=description.strip(),
        type=bill_type,
        amount_cents=parse_money_to_cents(amount_str),
        due_date=due_date,
        account_id=account_id or None,
        category_id=category_id or None,
        status=BillStatus.PENDING,
    )
    db.session.add(bill)
    db.session.commit()
    return bill


def update_bill(
    bill: Bill,
    description: str,
    bill_type: str,
    amount_str: str,
    due_date: date,
    account_id: int | None = None,
    category_id: int | None = None,
) -> Bill:
    bill.description = description.strip()
    bill.type = bill_type
    bill.amount_cents = parse_money_to_cents(amount_str)
    bill.due_date = due_date
    bill.account_id = account_id or None
    bill.category_id = category_id or None
    db.session.commit()
    return bill


def pay_bill(bill: Bill, user_id: int, account_id: int, paid_date: date | None = None):
    from app.transactions.services import create_transaction

    if paid_date is None:
        paid_date = date.today()

    if bill.type == BillType.PAYABLE:
        tx_type = TransactionType.EXPENSE
        new_status = BillStatus.PAID
        tx_status = TransactionStatus.PAID
    else:
        tx_type = TransactionType.INCOME
        new_status = BillStatus.RECEIVED
        tx_status = TransactionStatus.RECEIVED

    tx = create_transaction(
        family_id=bill.family_id,
        user_id=user_id,
        account_id=account_id,
        tx_type=tx_type,
        description=bill.description,
        amount_str=format_cents_to_money(bill.amount_cents),
        transaction_date=paid_date,
        category_id=bill.category_id,
        status=tx_status,
    )
    bill.status = new_status
    db.session.commit()
    return tx


def cancel_bill(bill: Bill) -> Bill:
    bill.status = BillStatus.CANCELED
    db.session.commit()
    return bill
