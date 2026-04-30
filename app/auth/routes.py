from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from . import auth_bp
from .forms import LoginForm, RegisterForm
from .services import register_user, authenticate
from ..utils.families import get_current_family


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    form = RegisterForm()
    if form.validate_on_submit():
        user = register_user(form.name.data, form.email.data, form.password.data)
        login_user(user)
        flash(f'Bem-vindo(a), {user.name.split()[0]}! Agora crie a sua família.', 'success')
        return redirect(url_for('families.new'))

    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = authenticate(form.email.data, form.password.data)
        if user:
            login_user(user, remember=form.remember.data)
            flash(f'Bem-vindo(a) de volta, {user.name.split()[0]}!', 'success')
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            if get_current_family(user) is None:
                return redirect(url_for('families.new'))
            return redirect(url_for('dashboard.index'))
        flash('E-mail ou senha incorretos.', 'danger')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('auth.login'))
