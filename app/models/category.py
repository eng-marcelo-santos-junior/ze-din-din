import enum
from datetime import datetime
from ..extensions import db


class CategoryType(str, enum.Enum):
    INCOME = 'INCOME'
    EXPENSE = 'EXPENSE'


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    family_id = db.Column(db.Integer, db.ForeignKey('families.id'), nullable=False, index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(10), nullable=False)
    color = db.Column(db.String(7), nullable=False, default='#6c757d')
    icon = db.Column(db.String(50), nullable=False, default='bi-tag')
    is_default = db.Column(db.Boolean, nullable=False, default=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    family = db.relationship('Family', backref=db.backref('categories', lazy='dynamic'))
    parent = db.relationship(
        'Category',
        remote_side='Category.id',
        backref=db.backref('subcategories', lazy='dynamic'),
    )

    def __repr__(self) -> str:
        return f'<Category {self.name}>'
