import re


def parse_money_to_cents(value: str) -> int:
    """Converte string monetária para centavos inteiros.

    Aceita formato pt-BR ("1.234,56") e en ("1234.56").
    """
    if not value:
        return 0
    value = str(value).strip()
    if ',' in value:
        # pt-BR: 1.234,56 → remove ponto de milhar, troca vírgula por ponto
        value = value.replace('.', '').replace(',', '.')
    else:
        # en: 1,234.56 → remove vírgula de milhar
        value = value.replace(',', '')
    value = re.sub(r'[^\d.\-]', '', value)
    if not value or value in ('.', '-', '-.'):
        return 0
    try:
        return round(float(value) * 100)
    except ValueError:
        return 0


def format_cents_to_money(cents: int) -> str:
    """Formata centavos inteiros para string no padrão pt-BR ("1.234,56")."""
    if cents is None:
        return '0,00'
    negative = cents < 0
    abs_val = abs(cents)
    reais = abs_val // 100
    centavos = abs_val % 100
    reais_str = f'{reais:,}'.replace(',', '.')
    result = f'{reais_str},{centavos:02d}'
    return f'-{result}' if negative else result
