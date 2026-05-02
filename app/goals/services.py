from app.extensions import db
from app.models.goal import Goal, GoalStatus
from app.utils.money import parse_money_to_cents


def get_goals(family_id: int, active_only: bool = False) -> list[Goal]:
    q = (
        db.select(Goal)
        .where(Goal.family_id == family_id)
        .order_by(Goal.status, Goal.created_at.desc())
    )
    if active_only:
        q = q.where(Goal.status == GoalStatus.ACTIVE)
    return db.session.scalars(q).all()


def get_goal(goal_id: int, family_id: int) -> Goal | None:
    return db.session.scalar(
        db.select(Goal).where(
            Goal.id == goal_id,
            Goal.family_id == family_id,
        )
    )


def create_goal(
    family_id: int,
    name: str,
    target_amount_str: str,
    target_date=None,
    account_id: int | None = None,
) -> Goal:
    goal = Goal(
        family_id=family_id,
        name=name.strip(),
        target_amount_cents=parse_money_to_cents(target_amount_str),
        current_amount_cents=0,
        target_date=target_date or None,
        account_id=account_id or None,
        status=GoalStatus.ACTIVE,
    )
    db.session.add(goal)
    db.session.commit()
    return goal


def update_goal(
    goal: Goal,
    name: str,
    target_amount_str: str,
    target_date=None,
    account_id: int | None = None,
) -> Goal:
    goal.name = name.strip()
    goal.target_amount_cents = parse_money_to_cents(target_amount_str)
    goal.target_date = target_date or None
    goal.account_id = account_id or None
    db.session.commit()
    return goal


def contribute_to_goal(goal: Goal, amount_str: str) -> Goal:
    amount = parse_money_to_cents(amount_str)
    if amount <= 0:
        return goal
    goal.current_amount_cents += amount
    if goal.current_amount_cents >= goal.target_amount_cents:
        goal.status = GoalStatus.COMPLETED
    db.session.commit()
    return goal


def cancel_goal(goal: Goal) -> Goal:
    goal.status = GoalStatus.CANCELED
    db.session.commit()
    return goal
