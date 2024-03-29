# -*- coding: utf-8 -*-


from decimal import Decimal as Dec
from dmon.money import Money
from dmon.currency import Currency


on_date = '2022-07-14'
previous_date = '2022-01-07'


def test_money_creation():
    # The Eur class will have euros as the default currency, and will
    # convert between currencies with the rates of on_date.
    Eur = Money(Currency.EUR, on=on_date)

    # The Aud class has Australian dollars as the default currency.
    Aud = Money(Currency.AUD, on=on_date)

    # The values are always stored in cents, and are available in any currency.
    assert Eur(23, '€').cents('eur') == 2300

    # The default currency is €
    assert Eur(23, '€').cents('eur') == 2300

    assert Eur(23).cents('EUR') == 2300
    assert Eur(23).cents() == 2300
    assert Eur(40).cents('usd') == Dec('4020.100502512562814070351759')
    assert Eur(40).cents(Currency.USD) == Dec('4020.100502512562814070351759')

    # Values can be created in any currency, independently of the
    # default currency of the class.
    assert Eur(20, '£') == Aud(20, '£')
    assert Eur(20, '£').default_currency != Aud(20, '£').default_currency

    # This hapens to be the conversion for on_date
    assert Eur(20.1, '$') == Eur(20, '€') == Eur(20)

    assert Eur(40).amount() == Dec('40')
    assert Eur(40).amount(Currency.USD, rounding=True) == Dec('40.2')
    assert Eur(40).amount(Currency.USD) == Dec('40.20100502512562814070351759')
    assert str(Eur(40).to(Currency.USD)) == '$40.20'
    assert str(Eur(40, '$')) == '$40.00'

    assert Eur(40).to('$').cents() == Dec('4020.100502512562814070351759')
    assert Eur(40).to('$').cents() == Eur(40).cents('$')

    assert Eur(40).to(Currency.AUD) == Aud(59.4) == Eur(59.4, 'aud')
    assert Eur(40).to(Currency.INR) == Aud(3198.76, 'inr')
    assert str(Eur(40).to(Currency.INR)) == '₹3198.76'

    cents, cur = Eur(20).as_tuple()
    assert Aud((cents, cur), amount_is_cents=True) == Eur(20)  # type: ignore


def test_money_comparisons():
    Eur = Money(Currency.EUR, on=on_date)
    Aud = Money(Currency.AUD, on=on_date)

    # Conversions do not affect comparisons
    assert Eur(40, '€').to(Currency.CAD) == Eur(40)

    assert Eur(40) == Aud(59.4)
    assert Eur(40) >= Aud(59.4)
    assert Eur(40) <= Aud(59.4)

    assert Eur(40.1) >= Aud(59.4)
    assert Eur(40.1) > Aud(59.4)

    assert Eur(40) <= Aud(59.5)
    assert Eur(40) < Aud(59.5)


def test_money_dates():
    Eur = Money(Currency.EUR, on=on_date)
    OldEur = Money('€', on=previous_date)

    assert OldEur(20) == Eur(20)  # we don't take inflation into account
    assert OldEur(20).to('$') != Eur(20).to('$')

    # We can override the default date when creating the instance:
    assert OldEur(20, on=on_date).to('$') == Eur(20).to('$')

    # The date of the converted value is inherited.
    assert OldEur(20).to('$').on_date == OldEur(20).on_date

    # The class names include the date, or latest if it is today
    # (which is the default when no date is assigned)
    assert type(Eur(10)).__name__ == 'Money_' + on_date
    assert type(OldEur(10)).__name__ == 'Money_' + previous_date

    TodaysEur = Money('€')
    assert type(TodaysEur(10)).__name__ == 'Money_latest'


def test_operations():
    Eur = Money(Currency.EUR, on=on_date)
    OldEur = Money('€', on=previous_date)
    Aud = Money(Currency.AUD, on=on_date)
    # An operation between two instances with different dates returns
    # an instance with the most recent date
    adds = OldEur(10) + Eur(30)
    assert adds.amount() == 40
    adds = Eur(30) + OldEur(10)
    assert adds.on_date == on_date

    # An operation between two instances with different currencies
    # returns a result on the default currency.
    assert (Eur(10, '$') + Eur(20, 'CAD')).currency == Currency.EUR

    assert sum(Eur(i) for i in range(10)) == Eur(45)
    assert Aud(10) + Eur(20) == Aud(39.70) == Eur(39.7, 'aud')
    assert Eur(20) + Aud(10) == Eur(26.73)

    assert Aud(10) + Eur(20) == Eur(20) + Aud(10)

    assert (Aud(10) + Eur(20)).currency == Currency.AUD
    assert (Eur(20) + Aud(10)).currency == Currency.EUR

    assert str(Eur(20, 'aud') + Eur(20, 'gbp')) == '€37.14'
    assert str(Aud(20, 'aud') + Aud(20, 'gbp')) == 'A$55.15'
    assert Eur(20, 'aud') + Eur(20, 'gbp') == Aud(20, 'aud') + Aud(20, 'gbp')

    Eur.to_date(previous_date)
    assert str(Eur(20, 'aud') + Eur(20, 'gbp')) == '€36.65'

    # They require conversion, and the default dates in Eur and Aud are different
    assert Eur(20, 'aud') + Eur(20, 'gbp') != Aud(20, 'aud') + Aud(20, 'gbp')

    assert 0.1 * Eur(10) == Eur(1)
    assert Eur(20) / 10 == Eur(2)
    assert Eur(20) / Eur(10) == Dec(2)


def test_output_currency():
    PD = Money('£', output_currency='$', on=on_date)
    assert str(PD(20)) == '$23.79'
    assert str(PD(20, '£')) == '$23.79'
    assert str(PD(20, 'gbp')) == '$23.79'
    assert str(PD(20, Currency.GBP)) == '$23.79'
    assert str(PD(20, Currency.USD)) == '$20.00'
