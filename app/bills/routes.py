from datetime import date, datetime
from flask import render_template, redirect, url_for, flash, g, abort, request
from flask_login import login_required, current_user
from . import bills_bp
from .forms import BillForm, PayBillForm
from .services import get_bills, get_bill, create_bill, update_bill, pay_bill, cancel_bill
from ..accounts.services import get_accounts
from ..categories.services import get_categories
from ..utils.decorators import family_required
from ..utils.money import format_cents_to_money


def _populate_form(form, family_id: int):
    accounts = get_accounts(family_id)
    form.account_id.choices = [(0, '— Selecione —')] + [(a.id, a.name) for a in accounts]
    cats = get_categories(family_id)
    form.category_id.choices = [(0, '— Sem categoria —')] + [(c.id, c.name) for c in cats]


@bills_bp.route('/bills')
@login_required
@family_required
def index():
    family_id = g.current_family.id
    tab = request.args.get('tab', 'pending')

    all_bills = get_bills(family_id)
    pending = [b for b in all_bills if b.status == 'PENDING']
    history = [b for b in all_bills if b.status != 'PENDING']

    pay_form = PayBillForm()
    pay_form.paid_date.data = date.today()
    accounts = get_accounts(family_id)
    pay_form.account_id.choices = [(a.id, a.name) for a in accounts]

    return render_template(
        'bills/index.html',
        pending=pending,
        history=history,
        tab=tab,
        pay_form=pay_form,
        accounts=accounts,
    )


@bills_bp.route('/bills/new', methods=['GET', 'POST'])
@login_required
@family_required
def new():
    form = BillForm()
    family_id = g.current_family.id
    _populate_form(form, family_id)

    if request.method == 'GET':
        form.type.data = request.args.get('type', 'PAYABLE')

    if form.validate_on_submit():
        account_id = form.account_id.data if form.account_id.data else None
        category_id = form.category_id.data if form.category_id.data else None
        bill = create_bill(
            family_id=family_id,
            description=form.description.data,
            bill_type=form.type.data,
            amount_str=form.amount.data,
            due_date=form.due_date.data,
            account_id=account_id,
            category_id=category_id,
        )
        flash(f'"{bill.description}" adicionada com sucesso.', 'success')
        return redirect(url_for('bills.index'))

    return render_template('bills/form.html', form=form, bill=None)


@bills_bp.route('/bills/<int:bill_id>/edit', methods=['GET', 'POST'])
@login_required
@family_required
def edit(bill_id: int):
    bill = get_bill(bill_id, g.current_family.id)
    if bill is None:
        abort(404)

    form = BillForm(obj=bill)
    family_id = g.current_family.id
    _populate_form(form, family_id)

    if form.validate_on_submit():
        account_id = form.account_id.data if form.account_id.data else None
        category_id = form.category_id.data if form.category_id.data else None
        update_bill(
            bill,
            description=form.description.data,
            bill_type=form.type.data,
            amount_str=form.amount.data,
            due_date=form.due_date.data,
            account_id=account_id,
            category_id=category_id,
        )
        flash(f'"{bill.description}" atualizada.', 'success')
        return redirect(url_for('bills.index'))

    if request.method == 'GET':
        form.amount.data = format_cents_to_money(bill.amount_cents)
        form.account_id.data = bill.account_id or 0
        form.category_id.data = bill.category_id or 0

    return render_template('bills/form.html', form=form, bill=bill)


@bills_bp.route('/bills/<int:bill_id>/pay', methods=['POST'])
@login_required
@family_required
def pay(bill_id: int):
    bill = get_bill(bill_id, g.current_family.id)
    if bill is None:
        abort(404)

    form = PayBillForm()
    accounts = get_accounts(g.current_family.id)
    form.account_id.choices = [(a.id, a.name) for a in accounts]

    if form.validate_on_submit():
        pay_bill(bill, current_user.id, form.account_id.data, form.paid_date.data)
        label = 'paga' if bill.type == 'PAYABLE' else 'recebida'
        flash(f'"{bill.description}" marcada como {label}. Transação criada.', 'success')
    else:
        flash('Erro ao registrar pagamento. Verifique os dados.', 'danger')

    return redirect(url_for('bills.index'))


@bills_bp.route('/bills/<int:bill_id>/cancel', methods=['POST'])
@login_required
@family_required
def cancel(bill_id: int):
    bill = get_bill(bill_id, g.current_family.id)
    if bill is None:
        abort(404)
    cancel_bill(bill)
    flash(f'"{bill.description}" cancelada.', 'warning')
    return redirect(url_for('bills.index'))
