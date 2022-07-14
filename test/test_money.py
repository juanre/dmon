# -*- coding: utf-8 -*-


from decimal import Decimal as Dec
from money.money import Money, Eur, Aud, TupleMoney, Currency

def test_money():
    M = Money()

    assert M(23) == Eur(23)
    assert M(23).in_currency('eur') == 2300
    assert M(40).in_currency('usd') == Dec('4020')

    assert Eur(40).to_currency_enum('usd') == Currency.USD

    assert Eur(40).amount() == Dec('40')
    assert Eur(40).amount(Currency.USD) == Dec('40.2')

    assert Eur(40).cents() == Dec('4000')

    assert Eur(40).to(Currency.AUD) == Aud(59.4)
    assert Eur(40).to(Currency.CAD).to(Currency.EUR) == Eur(40)

    assert TupleMoney((2000, 'eur')) == Eur(20)
