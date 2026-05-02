from datetime import date, datetime
from flask import render_template, redirect, url_for, flash, g, abort, request
from flask_login import login_required, current_user
from . import transactions_bp
from .forms import TransactionForm, TransferForm
from .services import (
    get_transactions, get_transaction, create_transaction,
    update_transaction, delete_transaction, duplicate_transaction,
    mark_as_paid, create_transfer, get_period_summary, TransactionFilters,
)
from ..accounts.services import get_accounts
from ..categories.services import get_categories
from ..utils.decorators import family_required
from ..utils.money import format_cents_to_money


def _build_form_choices(form, family_id: int):
    accounts = get_accounts(family_id)
    form.account_id.choices = [(a.id, a.name) for a in accounts]

    all_cats = get_categories(family_id)
    form.category_id.choices = [(0, '— Sem categoria —')] + [
        (c.id, f'{"  └ " if c.parent_id else ""}{c.name}') for c in all_cats
    ]


def _build_filters_from_request() -> TransactionFilters:
    def parse_date(val):
        try:
            return datetime.strptime(val, '%Y-%m-%d').date() if val else None
        except ValueError:
            return None

    return TransactionFilters(
        start_date=parse_date(request.args.get('start_date')),
        end_date=parse_date(request.args.get('end_date')),
        type=request.args.get('type') or None,
        account_id=int(request.args.get('account_id')) if request.args.get('account_id') else None,
        category_id=int(request.args.get('category_id')) if request.args.get('category_id') else None,
        status=request.args.get('status') or None,
        search=request.args.get('q') or None,
    )


@transactions_bp.route('/transactions')
@login_required
@family_required
def index():
    family = g.current_family
    filters = _build_filters_from_request()
    page = request.args.get('page', 1, type=int)
    pagination = get_transactions(family.id, filters=filters, page=page)
    summary = get_period_summary(family.id, filters)
    accounts = get_accounts(family.id)
    categories = get_categories(family.id)
    def page_url(p):
        a = request.args.to_dict()
        a['page'] = str(p)
        return url_for('transactions.index', **a)

    return render_template(
        'transactions/index.html',
        pagination=pagination,
        filters=filters,
        summary=summary,
        accounts=accounts,
        categories=categories,
        fmt=format_cents_to_money,
        args=request.args,
        page_url=page_url,
    )


@transactions_bp.route('/transactions/new', methods=['GET', 'POST'])
@login_required
@family_required
def new():
    form = TransactionForm()
    _build_form_choices(form, g.current_family.id)

    if form.validate_on_submit():
        cat_id = form.category_id.data if form.category_id.data else None
        tx = create_transaction(
            family_id=g.current_family.id,
            user_id=current_user.id,
            account_id=form.account_id.data,
            tx_type=form.type.data,
            description=form.description.data,
            amount_str=form.amount.data,
            transaction_date=form.transaction_date.data,
            category_id=cat_id,
            competence_date=form.competence_date.data,
            status=form.status.data,
            payment_method=form.payment_method.data,
            notes=form.notes.data,
        )
        flash(f'Transação "{tx.description}" registrada.', 'success')
        return redirect(url_for('transactions.index'))

    return render_template('transactions/form.html', form=form, transaction=None)


@transactions_bp.route('/transactions/<int:tx_id>/edit', methods=['GET', 'POST'])
@login_required
@family_required
def edit(tx_id: int):
    tx = get_transaction(tx_id, g.current_family.id)
    if tx is None:
        abort(404)

    form = TransactionForm(obj=tx)
    _build_form_choices(form, g.current_family.id)

    if form.validate_on_submit():
        cat_id = form.category_id.data if form.category_id.data else None
        update_transaction(
            tx,
            account_id=form.account_id.data,
            tx_type=form.type.data,
            description=form.description.data,
            amount_str=form.amount.data,
            transaction_date=form.transaction_date.data,
            category_id=cat_id,
            competence_date=form.competence_date.data,
            status=form.status.data,
            payment_method=form.payment_method.data,
            notes=form.notes.data,
        )
        flash(f'Transação "{tx.description}" atualizada.', 'success')
        return redirect(url_for('transactions.index'))

    if request.method == 'GET':
        form.amount.data = format_cents_to_money(abs(tx.amount_cents))
        form.account_id.data = tx.account_id
        form.category_id.data = tx.category_id or 0

    return render_template('transactions/form.html', form=form, transaction=tx)


@transactions_bp.route('/transactions/<int:tx_id>/delete', methods=['POST'])
@login_required
@family_required
def delete(tx_id: int):
    tx = get_transaction(tx_id, g.current_family.id)
    if tx is None:
        abort(404)
    desc = tx.description
    delete_transaction(tx)
    flash(f'Transação "{desc}" excluída.', 'warning')
    return redirect(url_for('transactions.index'))


@transactions_bp.route('/transactions/<int:tx_id>/duplicate', methods=['POST'])
@login_required
@family_required
def duplicate(tx_id: int):
    tx = get_transaction(tx_id, g.current_family.id)
    if tx is None:
        abort(404)
    copy = duplicate_transaction(tx, date.today())
    flash(f'Transação "{copy.description}" duplicada.', 'success')
    return redirect(url_for('transactions.index'))


@transactions_bp.route('/transactions/<int:tx_id>/mark-as-paid', methods=['POST'])
@login_required
@family_required
def mark_paid(tx_id: int):
    tx = get_transaction(tx_id, g.current_family.id)
    if tx is None:
        abort(404)
    mark_as_paid(tx)
    flash(f'"{tx.description}" marcada como paga/recebida.', 'success')
    return redirect(url_for('transactions.index'))


@transactions_bp.route('/transactions/transfer', methods=['GET', 'POST'])
@login_required
@family_required
def transfer():
    form = TransferForm()
    accounts = get_accounts(g.current_family.id)
    choices = [(a.id, a.name) for a in accounts]
    form.from_account_id.choices = choices
    form.to_account_id.choices = choices

    if form.validate_on_submit():
        if form.from_account_id.data == form.to_account_id.data:
            flash('As contas de origem e destino devem ser diferentes.', 'danger')
            return render_template('transactions/transfer.html', form=form)

        create_transfer(
            family_id=g.current_family.id,
            user_id=current_user.id,
            from_account_id=form.from_account_id.data,
            to_account_id=form.to_account_id.data,
            amount_str=form.amount.data,
            description=form.description.data,
            transaction_date=form.transaction_date.data,
            notes=form.notes.data,
        )
        flash('Transferência realizada com sucesso.', 'success')
        return redirect(url_for('transactions.index'))

    return render_template('transactions/transfer.html', form=form)
