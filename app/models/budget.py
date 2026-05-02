from datetime import datetime
from ..extensions import db


class Budget(db.Model):
    __tablename__ = 'budgets'

    id = db.Column(db.Integer, primary_key=True)
    family_id = db.Column(db.Integer, db.ForeignKey('families.id'), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False, index=True)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    planned_amount_cents = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    family = db.relationship('Family', backref=db.backref('budgets', lazy='dynamic'))
    category = db.relationship('Category', backref=db.backref('budgets', lazy='dynamic'))

    __table_args__ = (
        db.UniqueConstraint('family_id', 'category_id', 'month', 'year', name='uq_budget'),
        db.Index('ix_budgets_family_month_year', 'family_id', 'month', 'year'),
    )

    def __repr__(self) -> str:
        return f'<Budget {self.category_id} {self.month}/{self.year}>'
