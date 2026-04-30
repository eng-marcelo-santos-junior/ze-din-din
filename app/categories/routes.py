from flask import render_template, redirect, url_for, flash, g, abort
from flask_login import login_required
from . import categories_bp
from .forms import CategoryForm
from .services import (
    get_categories, get_category, create_category,
    update_category, archive_category,
)
from ..utils.decorators import family_required


def _populate_parent_choices(form, family_id: int, current_type: str, exclude_id: int = None):
    parents = get_categories(family_id, category_type=current_type, parent_only=True)
    choices = [(0, '— Nenhuma (categoria raiz) —')]
    choices += [
        (c.id, c.name) for c in parents
        if c.id != exclude_id
    ]
    form.parent_id.choices = choices


@categories_bp.route('/categories')
@login_required
@family_required
def index():
    family = g.current_family
    income = get_categories(family.id, category_type='INCOME')
    expense = get_categories(family.id, category_type='EXPENSE')
    return render_template('categories/index.html', income=income, expense=expense)


@categories_bp.route('/categories/new', methods=['GET', 'POST'])
@login_required
@family_required
def new():
    form = CategoryForm()
    current_type = form.type.data or 'EXPENSE'
    _populate_parent_choices(form, g.current_family.id, current_type)

    if form.validate_on_submit():
        create_category(
            family_id=g.current_family.id,
            name=form.name.data,
            category_type=form.type.data,
            color=form.color.data,
            icon=form.icon.data,
            parent_id=form.parent_id.data if form.parent_id.data else None,
        )
        flash('Categoria criada com sucesso.', 'success')
        return redirect(url_for('categories.index'))

    return render_template('categories/form.html', form=form, category=None)


@categories_bp.route('/categories/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
@family_required
def edit(category_id: int):
    category = get_category(category_id, g.current_family.id)
    if category is None:
        abort(404)

    form = CategoryForm(obj=category)
    _populate_parent_choices(form, g.current_family.id, category.type, exclude_id=category_id)

    if form.validate_on_submit():
        update_category(
            category,
            name=form.name.data,
            category_type=form.type.data,
            color=form.color.data,
            icon=form.icon.data,
            parent_id=form.parent_id.data if form.parent_id.data else None,
        )
        flash(f'Categoria "{category.name}" atualizada.', 'success')
        return redirect(url_for('categories.index'))

    if form.parent_id.data is None:
        form.parent_id.data = category.parent_id or 0

    return render_template('categories/form.html', form=form, category=category)


@categories_bp.route('/categories/<int:category_id>/archive', methods=['POST'])
@login_required
@family_required
def archive(category_id: int):
    category = get_category(category_id, g.current_family.id)
    if category is None:
        abort(404)
    archive_category(category)
    flash(f'Categoria "{category.name}" arquivada.', 'info')
    return redirect(url_for('categories.index'))
