from datetime import date
from flask import render_template, redirect, url_for, flash, g, abort, request
from flask_login import login_required
from . import budgets_bp
from .forms import BudgetForm
from .services import (
    get_budgets, get_budget, get_budget_overview,
    create_budget, update_budget, delete_budget,
    copy_previous_month_budget,
)
from ..categories.services import get_categories
from ..utils.decorators import family_required
from ..utils.money import format_cents_to_money


@budgets_bp.route('/budgets')
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

    family_id = g.current_family.id
    overview = get_budget_overview(family_id, month, year)

    total_planned = sum(item['budget'].planned_amount_cents for item in overview)
    total_realized = sum(item['realized_cents'] for item in overview)

    return render_template(
        'budgets/index.html',
        overview=overview,
        month=month,
        year=year,
        total_planned=total_planned,
        total_realized=total_realized,
    )


@budgets_bp.route('/budgets/new', methods=['GET', 'POST'])
@login_required
@family_required
def new():
    form = BudgetForm()
    family_id = g.current_family.id
    expense_cats = get_categories(family_id, category_type='EXPENSE')
    form.category_id.choices = [(c.id, c.name) for c in expense_cats]

    today = date.today()
    if request.method == 'GET':
        form.month.data = int(request.args.get('month', today.month))
        form.year.data = int(request.args.get('year', today.year))

    if form.validate_on_submit():
        budget = create_budget(
            family_id=family_id,
            category_id=form.category_id.data,
            month=form.month.data,
            year=form.year.data,
            planned_amount_str=form.planned_amount.data,
        )
        flash('Orçamento salvo com sucesso.', 'success')
        return redirect(url_for(
            'budgets.index',
            month=budget.month,
            year=budget.year,
        ))

    return render_template('budgets/form.html', form=form, budget=None)


@budgets_bp.route('/budgets/<int:budget_id>/edit', methods=['GET', 'POST'])
@login_required
@family_required
def edit(budget_id: int):
    budget = get_budget(budget_id, g.current_family.id)
    if budget is None:
        abort(404)

    form = BudgetForm(obj=budget)
    family_id = g.current_family.id
    expense_cats = get_categories(family_id, category_type='EXPENSE')
    form.category_id.choices = [(c.id, c.name) for c in expense_cats]

    if form.validate_on_submit():
        update_budget(budget, form.planned_amount.data)
        flash('Orçamento atualizado.', 'success')
        return redirect(url_for('budgets.index', month=budget.month, year=budget.year))

    if request.method == 'GET':
        form.planned_amount.data = format_cents_to_money(budget.planned_amount_cents)
        form.category_id.data = budget.category_id
        form.month.data = budget.month
        form.year.data = budget.year

    return render_template('budgets/form.html', form=form, budget=budget)


@budgets_bp.route('/budgets/<int:budget_id>/delete', methods=['POST'])
@login_required
@family_required
def delete(budget_id: int):
    budget = get_budget(budget_id, g.current_family.id)
    if budget is None:
        abort(404)
    month, year = budget.month, budget.year
    delete_budget(budget)
    flash('Orçamento removido.', 'warning')
    return redirect(url_for('budgets.index', month=month, year=year))


@budgets_bp.route('/budgets/copy-previous', methods=['POST'])
@login_required
@family_required
def copy_previous():
    try:
        month = int(request.form.get('month', date.today().month))
        year = int(request.form.get('year', date.today().year))
    except (ValueError, TypeError):
        month, year = date.today().month, date.today().year

    copied = copy_previous_month_budget(g.current_family.id, month, year)
    if copied:
        flash(f'{copied} orçamento(s) copiado(s) do mês anterior.', 'success')
    else:
        flash('Nenhum orçamento novo para copiar (mês anterior vazio ou já existente).', 'info')
    return redirect(url_for('budgets.index', month=month, year=year))
