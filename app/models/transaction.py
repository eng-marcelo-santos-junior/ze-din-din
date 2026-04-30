import enum
from datetime import datetime, date as date_type
from ..extensions import db


class TransactionType(str, enum.Enum):
    INCOME = 'INCOME'
    EXPENSE = 'EXPENSE'
    TRANSFER = 'TRANSFER'
    ADJUSTMENT = 'ADJUSTMENT'
    REFUND = 'REFUND'


class TransactionStatus(str, enum.Enum):
    PENDING = 'PENDING'
    PAID = 'PAID'
    RECEIVED = 'RECEIVED'
    CANCELED = 'CANCELED'


class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    family_id = db.Column(db.Integer, db.ForeignKey('families.id'), nullable=False, index=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(12), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    # Signed integer: positive = credit (income/inflow), negative = debit (expense/outflow)
    amount_cents = db.Column(db.Integer, nullable=False)
    transaction_date = db.Column(db.Date, nullable=False, index=True)
    competence_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(10), nullable=False, default=TransactionStatus.PAID)
    payment_method = db.Column(db.String(30), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    transfer_group_id = db.Column(db.String(36), nullable=True, index=True)
    installment_group_id = db.Column(db.String(36), nullable=True)
    recurring_rule_id = db.Column(db.String(36), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    family = db.relationship('Family', backref=db.backref('transactions', lazy='dynamic'))
    account = db.relationship('Account', backref=db.backref('transactions', lazy='dynamic'))
    category = db.relationship('Category', backref=db.backref('transactions', lazy='dynamic'))
    user = db.relationship('User', backref=db.backref('transactions', lazy='dynamic'))

    @property
    def display_amount_cents(self) -> int:
        return abs(self.amount_cents)

    @property
    def is_transfer(self) -> bool:
        return self.transfer_group_id is not None

    def __repr__(self) -> str:
        return f'<Transaction {self.type} {self.amount_cents}>'
