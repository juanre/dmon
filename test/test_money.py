# -*- coding: utf-8 -*-


from decimal import Decimal as Dec
from money.money import Money, TupleMoney, Currency


def test_money():
    on_date = '2022-07-14'
    Eur = Money(Currency.EUR, on=on_date)
    Aud = Money(Currency.AUD, on=on_date)

    assert Eur(23).in_currency('eur') == 2300
    assert Eur(40).in_currency('usd') == \
        Dec('4020.100502512562457013700623')

    assert Eur(40).to_currency_enum('usd') == Currency.USD

    assert Eur(40).amount() == Dec('40')
    assert Eur(40).amount(Currency.USD) == Dec('40.2')

    assert Eur(40).cents() == Dec('4000')

    assert Eur(40).to(Currency.AUD) == Aud(59.4)
    assert Eur(40).to(Currency.CAD).to(Currency.EUR) == Eur(40)

    assert TupleMoney((2000, 'eur')) == Eur(20)
    assert type(Eur(10)).__name__ == 'Money_' + on_date
