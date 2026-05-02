from flask import render_template, redirect, url_for, flash, g
from flask_login import login_required, current_user
from . import families_bp
from .forms import FamilyForm
from .services import create_family, get_members, update_family
from ..utils.families import get_current_family
from ..utils.decorators import family_required, role_required
from ..models.family import FamilyRole


@families_bp.route('/families/new', methods=['GET', 'POST'])
@login_required
def new():
    if get_current_family(current_user) is not None:
        return redirect(url_for('dashboard.index'))

    form = FamilyForm()
    if form.validate_on_submit():
        family = create_family(form.name.data, form.currency.data, current_user.id)
        flash(f'Família "{family.name}" criada com sucesso! Bem-vindo(a).', 'success')
        return redirect(url_for('dashboard.index'))

    return render_template('families/new.html', form=form)


@families_bp.route('/families/settings', methods=['GET', 'POST'])
@login_required
@family_required
def settings():
    family = g.current_family
    form = FamilyForm(obj=family)
    form.submit.label.text = 'Salvar alterações'

    if form.validate_on_submit():
        update_family(family, form.name.data, form.currency.data)
        flash('Configurações da família atualizadas.', 'success')
        return redirect(url_for('families.settings'))

    return render_template('families/settings.html', form=form, family=family)


@families_bp.route('/families/members')
@login_required
@family_required
def members():
    family = g.current_family
    member_list = get_members(family.id)
    return render_template('families/members.html', family=family, members=member_list)
