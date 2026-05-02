import enum
from datetime import datetime
from ..extensions import db


class AccountType(str, enum.Enum):
    CHECKING = 'CHECKING'
    SAVINGS = 'SAVINGS'
    CASH = 'CASH'
    WALLET = 'WALLET'
    INVESTMENT = 'INVESTMENT'
    CREDIT_CARD = 'CREDIT_CARD'


class AccountVisibility(str, enum.Enum):
    SHARED = 'SHARED'
    PRIVATE = 'PRIVATE'


ACCOUNT_TYPE_LABELS = {
    AccountType.CHECKING: 'Conta Corrente',
    AccountType.SAVINGS: 'Poupança',
    AccountType.CASH: 'Dinheiro em Espécie',
    AccountType.WALLET: 'Carteira Digital',
    AccountType.INVESTMENT: 'Investimento',
    AccountType.CREDIT_CARD: 'Cartão de Crédito',
}

ACCOUNT_TYPE_ICONS = {
    AccountType.CHECKING: 'bi-bank',
    AccountType.SAVINGS: 'bi-piggy-bank',
    AccountType.CASH: 'bi-cash-stack',
    AccountType.WALLET: 'bi-wallet2',
    AccountType.INVESTMENT: 'bi-graph-up-arrow',
    AccountType.CREDIT_CARD: 'bi-credit-card',
}


class Account(db.Model):
    __tablename__ = 'accounts'

    id = db.Column(db.Integer, primary_key=True)
    family_id = db.Column(db.Integer, db.ForeignKey('families.id'), nullable=False, index=True)
    owner_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False, default=AccountType.CHECKING)
    institution = db.Column(db.String(100))
    initial_balance_cents = db.Column(db.Integer, nullable=False, default=0)
    current_balance_cents = db.Column(db.Integer, nullable=False, default=0)
    currency = db.Column(db.String(3), nullable=False, default='BRL')
    color = db.Column(db.String(7), nullable=False, default='#0d6efd')
    icon = db.Column(db.String(50), nullable=False, default='bi-bank')
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    visibility = db.Column(db.String(10), nullable=False, default=AccountVisibility.SHARED)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    family = db.relationship('Family', backref=db.backref('accounts', lazy='dynamic'))
    owner = db.relationship('User', backref=db.backref('accounts', lazy='dynamic'))

    def __repr__(self) -> str:
        return f'<Account {self.name}>'
