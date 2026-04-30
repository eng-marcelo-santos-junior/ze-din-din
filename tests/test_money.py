import pytest
from app.utils.money import parse_money_to_cents, format_cents_to_money


class TestParseMoneyToCents:
    def test_formato_ptbr(self):
        assert parse_money_to_cents('1.234,56') == 123456

    def test_formato_simples(self):
        assert parse_money_to_cents('1234,56') == 123456

    def test_formato_en(self):
        assert parse_money_to_cents('1234.56') == 123456

    def test_valor_inteiro(self):
        assert parse_money_to_cents('100') == 10000

    def test_valor_zero(self):
        assert parse_money_to_cents('0') == 0
        assert parse_money_to_cents('0,00') == 0

    def test_valor_vazio(self):
        assert parse_money_to_cents('') == 0
        assert parse_money_to_cents(None) == 0

    def test_valor_negativo(self):
        assert parse_money_to_cents('-50,00') == -5000

    def test_centavos_apenas(self):
        assert parse_money_to_cents('0,99') == 99

    def test_milhar_ptbr(self):
        assert parse_money_to_cents('10.000,00') == 1000000

    def test_string_invalida(self):
        assert parse_money_to_cents('abc') == 0

    def test_valor_pequeno(self):
        assert parse_money_to_cents('1,50') == 150


class TestFormatCentsToMoney:
    def test_zero(self):
        assert format_cents_to_money(0) == '0,00'

    def test_valor_simples(self):
        assert format_cents_to_money(150) == '1,50'

    def test_valor_inteiro(self):
        assert format_cents_to_money(10000) == '100,00'

    def test_milhar(self):
        assert format_cents_to_money(123456) == '1.234,56'

    def test_negativo(self):
        assert format_cents_to_money(-5000) == '-50,00'

    def test_none(self):
        assert format_cents_to_money(None) == '0,00'

    def test_grande_valor(self):
        assert format_cents_to_money(1000000) == '10.000,00'

    def test_round_trip(self):
        original = '5.678,90'
        cents = parse_money_to_cents(original)
        assert format_cents_to_money(cents) == original
