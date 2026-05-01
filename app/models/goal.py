import enum
from datetime import datetime
from ..extensions import db


class GoalStatus(str, enum.Enum):
    ACTIVE = 'ACTIVE'
    COMPLETED = 'COMPLETED'
    CANCELED = 'CANCELED'


class Goal(db.Model):
    __tablename__ = 'goals'

    id = db.Column(db.Integer, primary_key=True)
    family_id = db.Column(db.Integer, db.ForeignKey('families.id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    target_amount_cents = db.Column(db.Integer, nullable=False)
    current_amount_cents = db.Column(db.Integer, nullable=False, default=0)
    target_date = db.Column(db.Date, nullable=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=True)
    status = db.Column(db.String(10), nullable=False, default=GoalStatus.ACTIVE)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    family = db.relationship('Family', backref=db.backref('goals', lazy='dynamic'))
    account = db.relationship('Account', backref=db.backref('goals', lazy='dynamic'))

    @property
    def progress_pct(self) -> int:
        if self.target_amount_cents <= 0:
            return 100
        return min(100, round(self.current_amount_cents / self.target_amount_cents * 100))

    @property
    def monthly_needed(self) -> int:
        from datetime import date
        if self.status != GoalStatus.ACTIVE or not self.target_date:
            return 0
        remaining = self.target_amount_cents - self.current_amount_cents
        if remaining <= 0:
            return 0
        today = date.today()
        months = (
            (self.target_date.year - today.year) * 12
            + self.target_date.month - today.month
        )
        if months <= 0:
            return remaining
        return remaining // months

    def __repr__(self) -> str:
        return f'<Goal {self.name!r} {self.progress_pct}%>'
