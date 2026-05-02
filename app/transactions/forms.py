from datetime import date
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SubmitField, DateField
from wtforms.validators import DataRequired, Length, Optional

TRANSACTION_TYPE_CHOICES = [
    ('EXPENSE', 'Despesa'),
    ('INCOME', 'Receita'),
    ('REFUND', 'Reembolso'),
    ('ADJUSTMENT', 'Ajuste'),
]

STATUS_CHOICES = [
    ('PAID', 'Pago'),
    ('RECEIVED', 'Recebido'),
    ('PENDING', 'Pendente'),
    ('CANCELED', 'Cancelado'),
]

PAYMENT_METHOD_CHOICES = [
    ('', '— Não informado —'),
    ('PIX', 'PIX'),
    ('TED', 'TED/DOC'),
    ('BOLETO', 'Boleto'),
    ('DEBIT_CARD', 'Cartão de Débito'),
    ('CREDIT_CARD', 'Cartão de Crédito'),
    ('CASH', 'Dinheiro'),
    ('CHECK', 'Cheque'),
    ('OTHER', 'Outros'),
]


class TransactionForm(FlaskForm):
    type = SelectField('Tipo', choices=TRANSACTION_TYPE_CHOICES, default='EXPENSE')
    description = StringField(
        'Descrição',
        validators=[DataRequired('Informe a descrição.'), Length(min=2, max=200)],
        render_kw={'placeholder': 'Ex: Supermercado, Salário de março'},
    )
    amount = StringField(
        'Valor',
        validators=[DataRequired('Informe o valor.')],
        render_kw={'placeholder': '0,00'},
    )
    transaction_date = DateField(
        'Data', validators=[DataRequired('Informe a data.')], default=date.today,
    )
    competence_date = DateField('Competência', validators=[Optional()])
    account_id = SelectField('Conta', coerce=int, validators=[DataRequired()])
    category_id = SelectField('Categoria', coerce=int, validators=[Optional()])
    status = SelectField('Status', choices=STATUS_CHOICES, default='PAID')
    payment_method = SelectField('Forma de pagamento', choices=PAYMENT_METHOD_CHOICES)
    notes = TextAreaField(
        'Observações', validators=[Optional(), Length(max=500)],
        render_kw={'rows': 3, 'placeholder': 'Informações adicionais...'},
    )
    submit = SubmitField('Salvar')


class TransferForm(FlaskForm):
    description = StringField(
        'Descrição',
        validators=[DataRequired()],
        render_kw={'placeholder': 'Ex: Transferência para reserva'},
    )
    amount = StringField(
        'Valor',
        validators=[DataRequired()],
        render_kw={'placeholder': '0,00'},
    )
    transaction_date = DateField('Data', validators=[DataRequired()], default=date.today)
    from_account_id = SelectField('Conta origem', coerce=int, validators=[DataRequired()])
    to_account_id = SelectField('Conta destino', coerce=int, validators=[DataRequired()])
    notes = TextAreaField('Observações', validators=[Optional(), Length(max=500)], render_kw={'rows': 3})
    submit = SubmitField('Transferir')
