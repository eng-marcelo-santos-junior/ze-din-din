from flask import render_template, redirect, url_for, flash, g, abort
from flask_login import login_required, current_user
from . import accounts_bp
from .forms import AccountForm
from .services import (
    get_accounts, get_account, create_account,
    update_account, archive_account, get_total_balance_cents,
)
from ..utils.decorators import family_required
from ..utils.money import format_cents_to_money


@accounts_bp.route('/accounts')
@login_required
@family_required
def index():
    family = g.current_family
    accounts = get_accounts(family.id)
    total_cents = get_total_balance_cents(family.id)
    return render_template(
        'accounts/index.html',
        accounts=accounts,
        total_cents=total_cents,
        fmt=format_cents_to_money,
    )


@accounts_bp.route('/accounts/new', methods=['GET', 'POST'])
@login_required
@family_required
def new():
    form = AccountForm()
    if form.validate_on_submit():
        account = create_account(
            family_id=g.current_family.id,
            owner_user_id=current_user.id,
            name=form.name.data,
            account_type=form.type.data,
            initial_balance=form.initial_balance.data or '0',
            currency=form.currency.data,
            institution=form.institution.data or '',
            color=form.color.data,
            visibility=form.visibility.data,
        )
        flash(f'Conta "{account.name}" criada com sucesso.', 'success')
        return redirect(url_for('accounts.index'))
    return render_template('accounts/form.html', form=form, account=None)


@accounts_bp.route('/accounts/<int:account_id>/edit', methods=['GET', 'POST'])
@login_required
@family_required
def edit(account_id: int):
    account = get_account(account_id, g.current_family.id)
    if account is None:
        abort(404)

    form = AccountForm(obj=account)
    if form.validate_on_submit():
        update_account(
            account,
            name=form.name.data,
            account_type=form.type.data,
            initial_balance=form.initial_balance.data or '0',
            currency=form.currency.data,
            institution=form.institution.data or '',
            color=form.color.data,
            visibility=form.visibility.data,
        )
        flash(f'Conta "{account.name}" atualizada.', 'success')
        return redirect(url_for('accounts.index'))

    if form.initial_balance.data is None:
        form.initial_balance.data = format_cents_to_money(account.initial_balance_cents)

    return render_template('accounts/form.html', form=form, account=account)


@accounts_bp.route('/accounts/<int:account_id>/archive', methods=['POST'])
@login_required
@family_required
def archive(account_id: int):
    account = get_account(account_id, g.current_family.id)
    if account is None:
        abort(404)
    archive_account(account)
    flash(f'Conta "{account.name}" arquivada.', 'info')
    return redirect(url_for('accounts.index'))
