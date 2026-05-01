from flask import render_template, redirect, url_for, flash, g, abort, request
from flask_login import login_required
from . import goals_bp
from .forms import GoalForm, ContributeForm
from .services import get_goals, get_goal, create_goal, update_goal, contribute_to_goal, cancel_goal
from ..accounts.services import get_accounts
from ..utils.decorators import family_required
from ..utils.money import format_cents_to_money
from ..models.goal import GoalStatus


@goals_bp.route('/goals')
@login_required
@family_required
def index():
    family_id = g.current_family.id
    goals = get_goals(family_id)
    contribute_form = ContributeForm()
    return render_template('goals/index.html', goals=goals, contribute_form=contribute_form)


@goals_bp.route('/goals/new', methods=['GET', 'POST'])
@login_required
@family_required
def new():
    form = GoalForm()
    family_id = g.current_family.id
    accounts = get_accounts(family_id)
    form.account_id.choices = [(0, '— Sem conta vinculada —')] + [(a.id, a.name) for a in accounts]

    if form.validate_on_submit():
        account_id = form.account_id.data if form.account_id.data else None
        goal = create_goal(
            family_id=family_id,
            name=form.name.data,
            target_amount_str=form.target_amount.data,
            target_date=form.target_date.data,
            account_id=account_id,
        )
        flash(f'Meta "{goal.name}" criada com sucesso.', 'success')
        return redirect(url_for('goals.index'))

    return render_template('goals/form.html', form=form, goal=None)


@goals_bp.route('/goals/<int:goal_id>/edit', methods=['GET', 'POST'])
@login_required
@family_required
def edit(goal_id: int):
    goal = get_goal(goal_id, g.current_family.id)
    if goal is None:
        abort(404)

    form = GoalForm(obj=goal)
    family_id = g.current_family.id
    accounts = get_accounts(family_id)
    form.account_id.choices = [(0, '— Sem conta vinculada —')] + [(a.id, a.name) for a in accounts]

    if form.validate_on_submit():
        account_id = form.account_id.data if form.account_id.data else None
        update_goal(
            goal,
            name=form.name.data,
            target_amount_str=form.target_amount.data,
            target_date=form.target_date.data,
            account_id=account_id,
        )
        flash(f'Meta "{goal.name}" atualizada.', 'success')
        return redirect(url_for('goals.index'))

    if request.method == 'GET':
        form.target_amount.data = format_cents_to_money(goal.target_amount_cents)
        form.account_id.data = goal.account_id or 0

    return render_template('goals/form.html', form=form, goal=goal)


@goals_bp.route('/goals/<int:goal_id>/contribute', methods=['POST'])
@login_required
@family_required
def contribute(goal_id: int):
    goal = get_goal(goal_id, g.current_family.id)
    if goal is None:
        abort(404)

    form = ContributeForm()
    if form.validate_on_submit():
        contribute_to_goal(goal, form.amount.data)
        if goal.status == GoalStatus.COMPLETED:
            flash(f'Parabéns! Meta "{goal.name}" concluída!', 'success')
        else:
            flash(f'Aporte registrado na meta "{goal.name}".', 'success')
    else:
        flash('Informe um valor válido para o aporte.', 'danger')

    return redirect(url_for('goals.index'))


@goals_bp.route('/goals/<int:goal_id>/cancel', methods=['POST'])
@login_required
@family_required
def cancel(goal_id: int):
    goal = get_goal(goal_id, g.current_family.id)
    if goal is None:
        abort(404)
    cancel_goal(goal)
    flash(f'Meta "{goal.name}" cancelada.', 'warning')
    return redirect(url_for('goals.index'))
