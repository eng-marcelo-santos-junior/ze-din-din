"""Testes unitários das propriedades computadas dos models.

Não precisam de acesso ao banco — testam lógica pura de instância.
"""
from datetime import date
import pytest

from app.models.goal import Goal, GoalStatus
from app.models.bill import Bill, BillStatus, BillType


# ── Goal.progress_pct ─────────────────────────────────────────────────────────

class TestGoalProgressPct:
    def _goal(self, target: int, current: int) -> Goal:
        g = Goal()
        g.target_amount_cents = target
        g.current_amount_cents = current
        g.status = GoalStatus.ACTIVE
        return g

    def test_zero_percent(self):
        assert self._goal(100000, 0).progress_pct == 0

    def test_fifty_percent(self):
        assert self._goal(100000, 50000).progress_pct == 50

    def test_hundred_percent(self):
        assert self._goal(100000, 100000).progress_pct == 100

    def test_never_exceeds_100(self):
        assert self._goal(100000, 200000).progress_pct == 100

    def test_target_zero_returns_100(self):
        assert self._goal(0, 0).progress_pct == 100

    def test_rounds_correctly(self):
        assert self._goal(300, 100).progress_pct == 33


# ── Goal.monthly_needed ───────────────────────────────────────────────────────

class TestGoalMonthlyNeeded:
    def test_no_target_date_returns_zero(self):
        g = Goal()
        g.target_amount_cents = 120000
        g.current_amount_cents = 0
        g.status = GoalStatus.ACTIVE
        g.target_date = None
        assert g.monthly_needed == 0

    def test_already_completed_returns_zero(self):
        g = Goal()
        g.target_amount_cents = 100000
        g.current_amount_cents = 100000
        g.status = GoalStatus.COMPLETED
        g.target_date = date(2027, 5, 1)
        assert g.monthly_needed == 0

    def test_calculates_monthly_amount(self):
        g = Goal()
        g.target_amount_cents = 120000  # R$ 1.200
        g.current_amount_cents = 0
        g.status = GoalStatus.ACTIVE
        g.target_date = date(2027, 5, 1)  # 12 months from TODAY (2026-05-01)
        assert g.monthly_needed == 10000  # R$ 100/month


# ── Bill.is_overdue ───────────────────────────────────────────────────────────

class TestBillIsOverdue:
    def _bill(self, due: date, status: str) -> Bill:
        b = Bill()
        b.due_date = due
        b.status = status
        return b

    def test_pending_past_due_is_overdue(self):
        b = self._bill(date(2026, 1, 1), BillStatus.PENDING)
        assert b.is_overdue is True

    def test_pending_future_is_not_overdue(self):
        b = self._bill(date(2027, 12, 31), BillStatus.PENDING)
        assert b.is_overdue is False

    def test_paid_past_due_is_not_overdue(self):
        b = self._bill(date(2026, 1, 1), BillStatus.PAID)
        assert b.is_overdue is False

    def test_canceled_is_not_overdue(self):
        b = self._bill(date(2026, 1, 1), BillStatus.CANCELED)
        assert b.is_overdue is False


# ── Bill.days_until_due ───────────────────────────────────────────────────────

class TestBillDaysUntilDue:
    def test_future_bill(self):
        b = Bill()
        b.due_date = date(2027, 5, 1)
        assert b.days_until_due == 365

    def test_past_bill_negative(self):
        b = Bill()
        b.due_date = date(2026, 4, 1)
        assert b.days_until_due == -30
