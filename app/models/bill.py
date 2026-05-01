import enum
from datetime import datetime, date as date_type
from ..extensions import db


class BillType(str, enum.Enum):
    PAYABLE = 'PAYABLE'
    RECEIVABLE = 'RECEIVABLE'


class BillStatus(str, enum.Enum):
    PENDING = 'PENDING'
    PAID = 'PAID'
    RECEIVED = 'RECEIVED'
    OVERDUE = 'OVERDUE'
    CANCELED = 'CANCELED'


class Bill(db.Model):
    __tablename__ = 'bills'

    id = db.Column(db.Integer, primary_key=True)
    family_id = db.Column(db.Integer, db.ForeignKey('families.id'), nullable=False, index=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    description = db.Column(db.String(200), nullable=False)
    amount_cents = db.Column(db.Integer, nullable=False)
    due_date = db.Column(db.Date, nullable=False, index=True)
    type = db.Column(db.String(12), nullable=False)
    status = db.Column(db.String(10), nullable=False, default=BillStatus.PENDING)
    recurrence_rule_id = db.Column(db.String(36), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    family = db.relationship('Family', backref=db.backref('bills', lazy='dynamic'))
    account = db.relationship('Account', backref=db.backref('bills', lazy='dynamic'))
    category = db.relationship('Category', backref=db.backref('bills', lazy='dynamic'))

    __table_args__ = (
        db.Index('ix_bills_family_due_date', 'family_id', 'due_date'),
    )

    @property
    def is_overdue(self) -> bool:
        from datetime import date
        return self.status == BillStatus.PENDING and self.due_date < date.today()

    @property
    def days_until_due(self) -> int:
        from datetime import date
        return (self.due_date - date.today()).days

    def __repr__(self) -> str:
        return f'<Bill {self.type} {self.description[:30]}>'
