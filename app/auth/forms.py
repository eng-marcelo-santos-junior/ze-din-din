from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError


class RegisterForm(FlaskForm):
    name = StringField(
        'Nome completo',
        validators=[DataRequired(message='Informe seu nome.'), Length(min=2, max=100)],
    )
    email = StringField(
        'E-mail',
        validators=[DataRequired(message='Informe seu e-mail.'), Email(), Length(max=150)],
    )
    password = PasswordField(
        'Senha',
        validators=[
            DataRequired(message='Informe uma senha.'),
            Length(min=8, message='A senha deve ter pelo menos 8 caracteres.'),
        ],
    )
    confirm_password = PasswordField(
        'Confirmar senha',
        validators=[
            DataRequired(message='Confirme sua senha.'),
            EqualTo('password', message='As senhas não coincidem.'),
        ],
    )
    submit = SubmitField('Criar conta')

    def validate_email(self, field: StringField) -> None:
        from ..extensions import db
        from ..models.user import User

        if db.session.scalar(db.select(User).where(User.email == field.data.lower())):
            raise ValidationError('Este e-mail já está cadastrado.')


class LoginForm(FlaskForm):
    email = StringField(
        'E-mail',
        validators=[DataRequired(message='Informe seu e-mail.'), Email()],
    )
    password = PasswordField(
        'Senha',
        validators=[DataRequired(message='Informe sua senha.')],
    )
    remember = BooleanField('Lembrar de mim')
    submit = SubmitField('Entrar')
