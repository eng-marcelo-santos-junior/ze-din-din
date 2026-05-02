from app.extensions import db
from app.models.account import Account, AccountType, AccountVisibility, ACCOUNT_TYPE_ICONS
from app.utils.money import parse_money_to_cents


def get_accounts(family_id: int, active_only: bool = True) -> list[Account]:
    q = db.select(Account).where(Account.family_id == family_id)
    if active_only:
        q = q.where(Account.is_active == True)
    q = q.order_by(Account.name)
    return db.session.scalars(q).all()


def get_account(account_id: int, family_id: int) -> Account | None:
    return db.session.scalar(
        db.select(Account).where(
            Account.id == account_id,
            Account.family_id == family_id,
        )
    )


def create_account(
    family_id: int,
    owner_user_id: int,
    name: str,
    account_type: str,
    initial_balance: str,
    currency: str = 'BRL',
    institution: str = '',
    color: str = '#0d6efd',
    visibility: str = AccountVisibility.SHARED,
) -> Account:
    balance_cents = parse_money_to_cents(initial_balance)
    icon = ACCOUNT_TYPE_ICONS.get(account_type, 'bi-bank')
    account = Account(
        family_id=family_id,
        owner_user_id=owner_user_id,
        name=name.strip(),
        type=account_type,
        institution=institution.strip() if institution else None,
        initial_balance_cents=balance_cents,
        current_balance_cents=balance_cents,
        currency=currency,
        color=color,
        icon=icon,
        visibility=visibility,
    )
    db.session.add(account)
    db.session.commit()
    return account


def update_account(
    account: Account,
    name: str,
    account_type: str,
    initial_balance: str,
    currency: str,
    institution: str,
    color: str,
    visibility: str,
) -> Account:
    new_initial_cents = parse_money_to_cents(initial_balance)
    # Preserve any balance change already applied (e.g. transactions)
    balance_delta = new_initial_cents - account.initial_balance_cents
    account.name = name.strip()
    account.type = account_type
    account.icon = ACCOUNT_TYPE_ICONS.get(account_type, 'bi-bank')
    account.initial_balance_cents = new_initial_cents
    account.current_balance_cents += balance_delta
    account.currency = currency
    account.institution = institution.strip() if institution else None
    account.color = color
    account.visibility = visibility
    db.session.commit()
    return account


def archive_account(account: Account) -> Account:
    account.is_active = False
    db.session.commit()
    return account


def get_total_balance_cents(family_id: int) -> int:
    accounts = get_accounts(family_id)
    return sum(a.current_balance_cents for a in accounts)
