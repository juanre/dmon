# -*- coding: utf-8 -*-


from decimal import Decimal as Dec
from dmon.money import Money, Currency


def test_money():
    on_date = '2022-07-14'
    Eur = Money(Currency.EUR, today=on_date)
    Aud = Money(Currency.AUD, today=on_date)

    assert Eur(23).in_currency('eur') == 2300
    assert Eur(40).in_currency('usd') == Dec('4020.100502512562832012897042')

    assert Eur(40).to_currency_enum('usd') == Currency.USD

    assert Eur(40).amount() == Dec('40')
    assert Eur(40).amount(Currency.USD, rounding=True) == Dec('40.2')
    assert Eur(40).amount(Currency.USD) == Dec('40.20100502512562832012897042')
    assert str(Eur(40).to(Currency.USD)) == '$40.20'

    assert Eur(40).cents() == Dec('4000')
    assert Eur(40).to('$').cents() == Dec('4020.100502512562832012897042')

    assert Eur(40).to(Currency.AUD) == Aud(59.4)
    assert Eur(40).to(Currency.CAD).to(Currency.EUR) == Eur(40)

    cents, cur, on = Eur(20).as_tuple()
    assert on == on_date
    assert Aud((cents, cur, on)) == Eur(20)

    old_date = '2022-01-07'
    OldEur = Money('€', today=old_date)
    old_cents, old_cur, old_on = OldEur(20).as_tuple()
    assert old_on == old_date

    # The date in the class takes precedence over the date in the instance.
    assert Eur((old_cents, old_cur, old_on)).to('$') == Eur(20).to('$')
    assert OldEur(20, on=on_date).to('$') != Eur(20).to('$')

    AnyTimeEur = Money('€')
    assert AnyTimeEur(OldEur(20).as_tuple()).to('$') != \
        AnyTimeEur(Eur(20).as_tuple()).to('$')

    assert type(Eur(10)).__name__ == 'Money_' + on_date
    assert type(OldEur(10)).__name__ == 'Money_' + old_date

    PD = Money('£', '$', today=on_date)
    assert str(PD(20)) == '$23.79'
    assert str(PD(20, '£')) == '$23.79'
    assert str(PD(20, 'gbp')) == '$23.79'
    assert str(PD(20, Currency.GBP)) == '$23.79'
    assert str(PD(20, Currency.USD)) == '$20.00'

    assert Eur(20) + 40 == Eur(60)
    assert 40 + Eur(20) == Eur(60)
    assert 0.1 * Eur(10) == Eur(1)
    assert Aud(10) + Eur(20) == Aud(39.70)
    assert Eur(20) + Aud(10) == Eur(26.73)

    assert Eur(20) / 10 == Eur(2)
    assert Eur(20) / Eur(10) == Dec(2)

    assert 20 / Eur(10) == Eur(2)
    assert 20 - Eur(10) == Eur(10)
