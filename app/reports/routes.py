import csv
import io
from datetime import date
from flask import render_template, request, g, Response
from flask_login import login_required
from . import reports_bp
from .services import (
    get_monthly_cash_flow,
    get_expenses_by_category,
    get_expenses_by_member,
    get_budget_vs_actual,
    get_biggest_expenses,
    get_net_worth_summary,
)
from ..accounts.services import get_accounts
from ..utils.decorators import family_required
from ..utils.money import format_cents_to_money

PT_MONTHS = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
             'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _filter_params():
    start_date = _parse_date(request.args.get('start_date'))
    end_date = _parse_date(request.args.get('end_date'))
    account_id = request.args.get('account_id', type=int)
    return start_date, end_date, account_id


def _csv_response(rows: list[list], filename: str) -> Response:
    buf = io.StringIO()
    csv.writer(buf).writerows(rows)
    return Response(
        buf.getvalue(),
        mimetype='text/csv; charset=utf-8',
        headers={'Content-Disposition': f'attachment; filename={filename}'},
    )


# ── Índice ────────────────────────────────────────────────────────────────────

@reports_bp.route('/reports')
@login_required
@family_required
def index():
    return render_template('reports/index.html')


# ── Fluxo de caixa ────────────────────────────────────────────────────────────

@reports_bp.route('/reports/cash-flow')
@login_required
@family_required
def cash_flow():
    num_months = max(1, min(24, request.args.get('months', 12, type=int)))
    data = get_monthly_cash_flow(g.current_family.id, num_months=num_months)
    return render_template('reports/cash_flow.html', data=data, num_months=num_months)


@reports_bp.route('/reports/cash-flow/export')
@login_required
@family_required
def cash_flow_export():
    num_months = max(1, min(24, request.args.get('months', 12, type=int)))
    data = get_monthly_cash_flow(g.current_family.id, num_months=num_months)
    rows = [['Mês', 'Receitas (R$)', 'Despesas (R$)', 'Resultado (R$)']]
    for r in data:
        rows.append([
            r['label'],
            format_cents_to_money(r['income_cents']),
            format_cents_to_money(r['expense_cents']),
            format_cents_to_money(r['result_cents']),
        ])
    return _csv_response(rows, 'fluxo_de_caixa.csv')


# ── Despesas por categoria ────────────────────────────────────────────────────

@reports_bp.route('/reports/categories')
@login_required
@family_required
def categories():
    family_id = g.current_family.id
    start_date, end_date, account_id = _filter_params()
    data = get_expenses_by_category(family_id, start_date, end_date, account_id)
    member_data = get_expenses_by_member(family_id, start_date, end_date)
    accounts = get_accounts(family_id)
    return render_template(
        'reports/categories.html',
        data=data,
        member_data=member_data,
        accounts=accounts,
        start_date=start_date,
        end_date=end_date,
        account_id=account_id,
    )


@reports_bp.route('/reports/categories/export')
@login_required
@family_required
def categories_export():
    start_date, end_date, account_id = _filter_params()
    data = get_expenses_by_category(g.current_family.id, start_date, end_date, account_id)
    rows = [['Categoria', 'Total (R$)', '% do Total']]
    for r in data:
        rows.append([r['name'], format_cents_to_money(r['total_cents']), f"{r['pct']}%"])
    return _csv_response(rows, 'despesas_por_categoria.csv')


# ── Orçamento vs. realizado ───────────────────────────────────────────────────

@reports_bp.route('/reports/budget')
@login_required
@family_required
def budget():
    today = date.today()
    try:
        month = max(1, min(12, int(request.args.get('month', today.month))))
        year = max(2000, min(2100, int(request.args.get('year', today.year))))
    except (ValueError, TypeError):
        month, year = today.month, today.year
    overview = get_budget_vs_actual(g.current_family.id, month, year)
    total_planned = sum(item['budget'].planned_amount_cents for item in overview)
    total_realized = sum(item['realized_cents'] for item in overview)
    return render_template(
        'reports/budget.html',
        overview=overview,
        month=month,
        year=year,
        pt_months=PT_MONTHS,
        total_planned=total_planned,
        total_realized=total_realized,
    )


@reports_bp.route('/reports/budget/export')
@login_required
@family_required
def budget_export():
    today = date.today()
    try:
        month = max(1, min(12, int(request.args.get('month', today.month))))
        year = max(2000, min(2100, int(request.args.get('year', today.year))))
    except (ValueError, TypeError):
        month, year = today.month, today.year
    overview = get_budget_vs_actual(g.current_family.id, month, year)
    rows = [['Categoria', 'Planejado (R$)', 'Realizado (R$)', 'Diferença (R$)', '% Utilizado', 'Status']]
    for item in overview:
        b = item['budget']
        diff = b.planned_amount_cents - item['realized_cents']
        rows.append([
            b.category.name,
            format_cents_to_money(b.planned_amount_cents),
            format_cents_to_money(item['realized_cents']),
            format_cents_to_money(diff),
            f"{item['pct']}%",
            item['health'],
        ])
    return _csv_response(rows, 'orcamento_vs_realizado.csv')


# ── Maiores despesas ──────────────────────────────────────────────────────────

@reports_bp.route('/reports/biggest-expenses')
@login_required
@family_required
def biggest_expenses():
    family_id = g.current_family.id
    start_date, end_date, account_id = _filter_params()
    transactions = get_biggest_expenses(family_id, start_date, end_date, account_id)
    accounts = get_accounts(family_id)
    return render_template(
        'reports/biggest_expenses.html',
        transactions=transactions,
        accounts=accounts,
        start_date=start_date,
        end_date=end_date,
        account_id=account_id,
    )


@reports_bp.route('/reports/biggest-expenses/export')
@login_required
@family_required
def biggest_expenses_export():
    start_date, end_date, account_id = _filter_params()
    transactions = get_biggest_expenses(g.current_family.id, start_date, end_date, account_id)
    rows = [['Data', 'Descrição', 'Categoria', 'Conta', 'Membro', 'Valor (R$)']]
    for tx in transactions:
        rows.append([
            tx.transaction_date.isoformat(),
            tx.description,
            tx.category.name if tx.category else '',
            tx.account.name if tx.account else '',
            tx.user.name if tx.user else '',
            format_cents_to_money(abs(tx.amount_cents)),
        ])
    return _csv_response(rows, 'maiores_despesas.csv')


# ── Patrimônio líquido ────────────────────────────────────────────────────────

@reports_bp.route('/reports/net-worth')
@login_required
@family_required
def net_worth():
    summary = get_net_worth_summary(g.current_family.id)
    return render_template('reports/net_worth.html', summary=summary)
