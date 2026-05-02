from datetime import date
from flask import render_template, g, request
from flask_login import login_required
from . import dashboard_bp
from ..utils.decorators import family_required
from .services import (
    DashboardFilters,
    get_total_balance,
    get_month_income,
    get_month_expenses,
    get_month_result,
    get_month_transaction_count,
    get_expenses_by_category,
    get_income_vs_expense_by_month,
    get_recent_transactions,
    get_top_expense_category,
)
from ..accounts.services import get_accounts


@dashboard_bp.route('/dashboard')
@login_required
@family_required
def index():
    today = date.today()

    try:
        month = int(request.args.get('month', today.month))
        year = int(request.args.get('year', today.year))
    except (ValueError, TypeError):
        month, year = today.month, today.year

    month = max(1, min(12, month))
    year = max(2000, min(2100, year))
    account_id = request.args.get('account_id', type=int)

    filters = DashboardFilters(month=month, year=year, account_id=account_id)
    family_id = g.current_family.id

    accounts = get_accounts(family_id)
    total_balance = get_total_balance(family_id)
    month_income = get_month_income(family_id, filters)
    month_expenses = get_month_expenses(family_id, filters)
    month_result = get_month_result(family_id, filters)
    tx_count = get_month_transaction_count(family_id, filters)
    expenses_by_category = get_expenses_by_category(family_id, filters)
    income_vs_expense = get_income_vs_expense_by_month(family_id)
    recent_transactions = get_recent_transactions(family_id)
    top_category = get_top_expense_category(family_id, filters)

    return render_template(
        'dashboard/index.html',
        family=g.current_family,
        filters=filters,
        accounts=accounts,
        total_balance=total_balance,
        month_income=month_income,
        month_expenses=month_expenses,
        month_result=month_result,
        tx_count=tx_count,
        expenses_by_category=expenses_by_category,
        income_vs_expense=income_vs_expense,
        recent_transactions=recent_transactions,
        top_category=top_category,
    )
