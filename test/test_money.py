# -*- coding: utf-8 -*-


from decimal import Decimal as Dec
from dmon.money import Money
from dmon.currency import Currency


date_a = "2022-07-14"
date_b = "2022-01-07"


def test_money_creation():
    # The Eur class will have euros as the default currency, and will
    # convert between currencies with the rates of date_a.
    Eur = Money(Currency.EUR, date_a)

    # The Aud class has Australian dollars as the default currency.
    Aud = Money(base_currency="A$", base_date=date_a)

    # The values are always stored in cents, and are available in any currency.
    assert Eur(23, "€").cents("eur") == 2300

    # The default currency is €
    assert Eur(23).cents("eur") == 2300

    assert Eur(23).cents("EUR") == 2300
    assert Eur(23).cents() == 2300
    assert Eur(40).cents("usd") == Dec("4020.100502512562832012897042")
    assert Eur(40).cents(Currency.USD) == Dec("4020.100502512562832012897042")

    # Values can be created in any currency, independently of the
    # default currency of the class.
    assert Eur(20, "£") == Aud(20, "£")
    assert Eur(20, "£").base_currency != Aud(20, "£").base_currency

    # This hapens to be the conversion for date_a
    assert Eur(20.1, "$") == Eur(20, "€") == Eur(20)

    assert Eur(40).amount() == Dec("40")
    assert Eur(40).amount(Currency.USD, rounding=True) == Dec("40.2")
    assert Eur(40).amount(Currency.USD) == Dec("40.20100502512562832012897042")
    assert str(Eur(40).to(Currency.USD)) == "$40.20"
    assert str(Eur(40, "$")) == "$40.00"

    assert Eur(40).to("$").cents() == Dec("4020.100502512562832012897042")
    assert Eur(40).to("$").cents() == Eur(40).cents("$")

    assert Eur(40).to(Currency.AUD) == Aud(59.4) == Eur(59.4, "aud")
    assert Eur(40).to(Currency.INR) == Aud(3198.76, "inr")
    assert str(Eur(40).to(Currency.INR)) == "₹3198.76"


def test_money_comparisons():
    Eur = Money(Currency.EUR, date_a)
    Aud = Money(Currency.AUD, date_a)

    # Conversions do not affect comparisons
    assert Eur(40, "€").to(Currency.CAD) == Eur(40)

    assert Eur(40) == Aud(59.4)
    assert Eur(40) >= Aud(59.4)
    assert Eur(40) <= Aud(59.4)

    assert Eur(40.1) >= Aud(59.4)
    assert Eur(40.1) > Aud(59.4)

    assert Eur(40) <= Aud(59.5)
    assert Eur(40) < Aud(59.5)


def test_money_dates():
    Eur = Money(Currency.EUR, date_a)
    OldEur = Money("€", date_b)

    assert OldEur(20) == Eur(20)

    # Comparisons are done in the base currency (in this case EUR). So
    # before the comparisons the two dollar amounts are converted to
    # euros, and they are both 20.
    assert OldEur(20).to("$") == Eur(20).to("$")

    # We can set the date when creating the instance:
    assert OldEur(20, on_date=date_a).to("$") == Eur(20).to("$")

    # The date of the converted value is inherited.
    assert OldEur(20).to("$").on_date == OldEur(20).on_date

    # The class names include the date, or latest if it is today
    # (which is the default when no date is assigned)
    assert type(Eur(10)).__name__ == "Money_" + date_a
    assert type(OldEur(10)).__name__ == "Money_" + date_b

    TodaysEur = Money("€")
    assert type(TodaysEur(10)).__name__ == "Money_current"


def test_operations():
    Eur = Money(Currency.EUR, date_a)
    OldEur = Money("€", date_b)
    Aud = Money(Currency.AUD, date_a)

    # An operation between two instances with different dates returns
    # an instance with the base date of the first element.
    adds = OldEur(10) + Eur(30)
    assert adds.amount() == 40
    adds = Eur(30) + OldEur(10)
    assert adds.on_date == Eur.base_date

    # An operation between two instances with different currencies
    # returns a result on the base currency.
    assert (Eur(10, "$") + Eur(20, "CAD")).currency == Currency.EUR

    # Changing the dates to which amounts are referenced changes the
    # result of operations. The $ and A$ are first converted to the
    # base currency (€ in this case) with the exchage rates of the day
    # they are referenced to.
    assert Eur(10, "$", date_a) + Eur(20, "CAD", date_a) != Eur(10, "$", date_b) + Eur(
        20, "CAD", date_b
    )
    assert (Eur(10, "$", date_a) + Eur(20, "CAD", date_a)).currency == Currency.EUR
    assert (Eur(10, "$", date_b) + Eur(20, "CAD", date_b)).on_date == Eur.base_date

    assert sum(Eur(i) for i in range(10)) == Eur(45)
    assert Aud(10) + Eur(20) == Aud(39.70) == Eur(39.7, "aud")
    assert Eur(20) + Aud(10) == Eur(26.73)

    assert Aud(10) + Eur(20) == Eur(20) + Aud(10)

    assert (Aud(10) + Eur(20)).currency == Currency.AUD
    assert (Eur(20) + Aud(10)).currency == Currency.EUR

    assert str(Eur(20, "aud") + Eur(20, "gbp")) == "€37.14"
    assert str(Aud(20, "aud") + Aud(20, "gbp")) == "A$55.15"
    assert Eur(20, "aud") + Eur(20, "gbp") == Aud(20, "aud") + Aud(20, "gbp")

    assert str(Eur(20, "aud", date_b) + Eur(20, "gbp", date_b)) == "€36.65"

    assert Eur(20, "aud") + Eur(20, "gbp") == Aud(20, "aud") + Aud(20, "gbp")

    assert 0.1 * Eur(10) == Eur(1)
    assert Eur(20) / 10 == Eur(2)
    assert Eur(20) / Eur(10) == Dec(2)


def test_output_currency():
    PD = Money("£", date_a, output_currency="$")
    assert str(PD(20)) == "$23.79"
    assert str(PD(20, "£")) == "$23.79"
    assert str(PD(20, "gbp")) == "$23.79"
    assert str(PD(20, Currency.GBP)) == "$23.79"
    assert str(PD(20, Currency.USD)) == "$20.00"


def test_repr():
    Eur = Money(Currency.EUR, date_a)

    assert repr(Eur(20, "£")) == "GBP 20.00"
    assert repr(Eur(20, "£", "2023-10-20")) == "2023-10-20 GBP 20.00"

    assert Eur.parse("GBP 20.00") == Eur(20, "£")

    # The base currency is the euro; a pound in 2023-10-20 is not the
    # same as a pound in date_a
    assert Eur.parse("2023-10-20 GBP 20.00") != Eur(20, "£")
    assert Eur.parse("2023-10-20 GBP 20.00") == Eur(20, "£", "2023-10-20")
