from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

CATEGORY_TYPE_CHOICES = [
    ('EXPENSE', 'Despesa'),
    ('INCOME', 'Receita'),
]

ICON_CHOICES = [
    ('bi-tag', 'Padrão'),
    ('bi-basket', 'Alimentação'),
    ('bi-house', 'Moradia'),
    ('bi-car-front', 'Transporte'),
    ('bi-heart-pulse', 'Saúde'),
    ('bi-book', 'Educação'),
    ('bi-controller', 'Lazer'),
    ('bi-cart', 'Mercado'),
    ('bi-lightning-charge', 'Energia'),
    ('bi-droplet', 'Água'),
    ('bi-wifi', 'Internet'),
    ('bi-play-circle', 'Assinaturas'),
    ('bi-receipt', 'Impostos'),
    ('bi-heart', 'Pets'),
    ('bi-briefcase', 'Trabalho'),
    ('bi-laptop', 'Tecnologia'),
    ('bi-graph-up-arrow', 'Investimentos'),
    ('bi-three-dots', 'Outros'),
]

COLOR_CHOICES = [
    ('#198754', 'Verde'),
    ('#0d6efd', 'Azul'),
    ('#dc3545', 'Vermelho'),
    ('#ffc107', 'Amarelo'),
    ('#6f42c1', 'Roxo'),
    ('#0dcaf0', 'Ciano'),
    ('#fd7e14', 'Laranja'),
    ('#6c757d', 'Cinza'),
    ('#795548', 'Marrom'),
]


class CategoryForm(FlaskForm):
    name = StringField(
        'Nome da categoria',
        validators=[DataRequired('Informe o nome da categoria.'), Length(min=2, max=100)],
        render_kw={'placeholder': 'Ex: Alimentação, Salário'},
    )
    type = SelectField('Tipo', choices=CATEGORY_TYPE_CHOICES, default='EXPENSE')
    parent_id = SelectField('Categoria pai', coerce=int, validators=[Optional()])
    color = SelectField('Cor', choices=COLOR_CHOICES, default='#6c757d')
    icon = SelectField('Ícone', choices=ICON_CHOICES, default='bi-tag')
    submit = SubmitField('Salvar categoria')
