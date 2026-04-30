from ..extensions import db
from ..models.user import User


def register_user(name: str, email: str, password: str) -> User:
    user = User(name=name, email=email.lower())
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def get_user_by_email(email: str) -> User | None:
    return db.session.scalar(db.select(User).where(User.email == email.lower()))


def authenticate(email: str, password: str) -> User | None:
    user = get_user_by_email(email)
    if user and user.is_active and user.check_password(password):
        return user
    return None
