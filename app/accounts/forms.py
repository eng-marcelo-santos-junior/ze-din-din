from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

ACCOUNT_TYPE_CHOICES = [
    ('CHECKING', 'Conta Corrente'),
    ('SAVINGS', 'Poupança'),
    ('CASH', 'Dinheiro em Espécie'),
    ('WALLET', 'Carteira Digital'),
    ('INVESTMENT', 'Investimento'),
    ('CREDIT_CARD', 'Cartão de Crédito'),
]

CURRENCY_CHOICES = [
    ('BRL', 'Real (R$)'),
    ('USD', 'Dólar ($)'),
    ('EUR', 'Euro (€)'),
]

VISIBILITY_CHOICES = [
    ('SHARED', 'Compartilhada — visível a todos os membros'),
    ('PRIVATE', 'Privada — somente você'),
]

COLOR_CHOICES = [
    ('#0d6efd', 'Azul'),
    ('#198754', 'Verde'),
    ('#dc3545', 'Vermelho'),
    ('#ffc107', 'Amarelo'),
    ('#6f42c1', 'Roxo'),
    ('#0dcaf0', 'Ciano'),
    ('#fd7e14', 'Laranja'),
    ('#6c757d', 'Cinza'),
    ('#795548', 'Marrom'),
    ('#212529', 'Preto'),
]


class AccountForm(FlaskForm):
    name = StringField(
        'Nome da conta',
        validators=[DataRequired('Informe o nome da conta.'), Length(min=2, max=100)],
        render_kw={'placeholder': 'Ex: Nubank, Carteira, Poupança'},
    )
    type = SelectField('Tipo', choices=ACCOUNT_TYPE_CHOICES, default='CHECKING')
    institution = StringField(
        'Instituição',
        validators=[Optional(), Length(max=100)],
        render_kw={'placeholder': 'Ex: Nubank, Itaú, Caixa'},
    )
    initial_balance = StringField(
        'Saldo inicial',
        validators=[Optional()],
        render_kw={'placeholder': '0,00'},
    )
    currency = SelectField('Moeda', choices=CURRENCY_CHOICES, default='BRL')
    color = SelectField('Cor', choices=COLOR_CHOICES, default='#0d6efd')
    visibility = SelectField('Visibilidade', choices=VISIBILITY_CHOICES, default='SHARED')
    submit = SubmitField('Salvar conta')
