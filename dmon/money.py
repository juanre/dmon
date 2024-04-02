# -*- coding: utf-8 -*-

from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from typing import Tuple, Union, Optional, ClassVar, Any, Type

from dmon.currency import Currency, CurrencySymbols, to_currency_enum
from dmon.rates import get_rates, parse_optional_date, format_date


Numeric = Union[int, float, Decimal]

_Cents = "c"


def cents_str(cents: Union[Numeric, str]) -> str:
    return str(cents) + _Cents


class BaseMoney:
    base_date: ClassVar[Optional[date]] = None
    base_currency: ClassVar[Currency] = Currency.USD
    output_currency: Optional[Currency] = None

    # Precision for checking equality, applied to the cents. A 0 is
    # equivalent to rounding cents.
    precision: ClassVar[int] = 0

    def __init__(
        self,
        amount: Union[str, Numeric],
        currency: Optional[Union[str, Currency]] = None,
        on_date: Optional[Union[date, str]] = None,
    ) -> None:
        """Initialize an instance, usually of a class derived from BaseMoney.

        Arguments:

        - amount: It can be a numeric value, or a string. The string
                  can either represent a numeric value, '12.34', or a
                  numeric value plus a 'c' as the last character,
                  '1234c'. In this last case the numeric value is
                  understood to be cents.

        - currency: If a string is provided it should be a
                    three-letter code of a currency in the Currency
                    enum, or a known currency symbol.

        - on_date: If a string is provided it should represent a date
                   in the form yyyy-mm-dd
        """
        self._cents: Decimal = (
            Decimal(amount[:-1])  # '2355c'
            if isinstance(amount, str) and amount[-1] == _Cents
            else (Decimal(amount) * 100)  # '23.55'
        )
        self.currency: Currency = to_currency_enum(currency or self.__class__.base_currency)
        self.on_date: Optional[date] = parse_optional_date(on_date)

    def cents(self, in_currency: Optional[Union[str, Currency]] = None) -> Decimal:
        """Converts the money amount to cents in the specified
        currency on the given date.

        Arguments:

        - in_currency: The target currency to convert to. If not
                       provided, the instance's currency is used.

        - on_date: The date for which the conversion rates should be
                   used. If not provided, the instance's original date
                   is used. If the date is None the current date is
                   used.

        Returns the amount in cents in the specified currency on the
        given date.

        The function first converts the provided currency (if any) to
        a Currency enum.  If the target currency is the same as the
        money's original currency, the amount in cents is returned
        directly.

        The amount is then converted to cents in the target currency
        by multiplying it with the ratio of the target currency rate
        to the original currency rate.

        """
        currency = to_currency_enum(in_currency or self.currency)
        if currency == self.currency:
            return self._cents

        rates_date = self.on_date or self.base_date or date.today()
        rates = get_rates(rates_date, currency, self.currency)

        if rates is None:
            raise RuntimeError("Could not find rates for {rates_date}")

        if rates[currency] is None:
            raise RuntimeError("Could not find conversion rate for ", currency)

        if rates[self.currency] is None:
            raise RuntimeError("Could not find conversion rate for ", self.currency)

        return self._cents * Decimal(str(rates[currency])) / Decimal(str(rates[self.currency]))

    def amount(
        self, currency: Optional[Union[str, Currency]] = None, rounding: bool = False
    ) -> Decimal:
        cents = self.cents(currency)
        return (Decimal(round(cents)) if rounding else cents) / Decimal("100")

    def to(self, currency: Union[str, Currency]) -> "BaseMoney":
        return self.__class__(cents_str(self.cents(currency)), currency, on_date=self.on_date)

    def on(self, on_date: str) -> "BaseMoney":
        return self.__class__(cents_str(self._cents), self.currency, on_date=on_date)

    def normalized_amounts(self, o: "BaseMoney") -> Tuple[Decimal, Decimal]:
        """Returns the two amounts in the base currency."""
        return (self.cents(self.base_currency), o.cents(self.base_currency))

    def __neg__(self) -> "BaseMoney":
        return self.__class__(cents_str(-self._cents), self.currency, on_date=self.on_date)

    def __add__(self, o: Union["BaseMoney", Numeric, str]) -> "BaseMoney":
        if not isinstance(o, BaseMoney):
            o = self.__class__(o, self.currency)

        v1, v2 = self.normalized_amounts(o)
        return self.__class__(cents_str(v1 + v2), self.base_currency, on_date=self.base_date)

    def __radd__(self, o: Union["BaseMoney", Numeric, str]) -> "BaseMoney":
        return self + o

    def __sub__(self, o: Union["BaseMoney", Numeric, str]) -> "BaseMoney":
        if not isinstance(o, BaseMoney):
            o = self.__class__(o, self.currency)

        v1, v2 = self.normalized_amounts(o)
        return self.__class__(cents_str(v1 - v2), self.base_currency, on_date=self.base_date)

    def __rsub__(self, o: Union["BaseMoney", Numeric, str]) -> "BaseMoney":
        return -self + o

    def __mul__(self, n: Numeric) -> "BaseMoney":
        return self.__class__(
            cents_str(self._cents * Decimal(n)), self.currency, on_date=self.on_date
        )

    __rmul__ = __mul__

    def __truediv__(self, o: Union["BaseMoney", Numeric]) -> Union["BaseMoney", Decimal]:
        if isinstance(o, BaseMoney):
            v1, v2 = self.normalized_amounts(o)
            return v1 / v2
            # return self._cents / n.to(self.currency).cents()

        return self.__class__(
            cents_str(self._cents / Decimal(o)), self.currency, on_date=self.on_date
        )

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, BaseMoney):
            return NotImplemented
        v1, v2 = self.normalized_amounts(o)
        precision_decimal = Decimal("1").scaleb(-self.precision)
        v1_quantized = v1.quantize(precision_decimal, rounding=ROUND_HALF_UP)
        v2_quantized = v2.quantize(precision_decimal, rounding=ROUND_HALF_UP)
        return v1_quantized == v2_quantized

    def __ne__(self, o: object) -> bool:
        eq_result = self.__eq__(o)
        if eq_result is NotImplemented:
            return NotImplemented
        return not eq_result

    def __gt__(self, o: "BaseMoney") -> bool:
        v1, v2 = self.normalized_amounts(o)
        return v1 > v2

    def __ge__(self, o: "BaseMoney") -> bool:
        eq_result = self.__eq__(o)
        if eq_result is NotImplemented:
            return NotImplemented
        return eq_result or self.__gt__(o)

    def __lt__(self, o: "BaseMoney") -> bool:
        v1, v2 = self.normalized_amounts(o)
        return v1 < v2

    def __le__(self, o: "BaseMoney") -> bool:
        eq_result = self.__eq__(o)
        if eq_result is NotImplemented:
            return NotImplemented
        return eq_result or self.__lt__(o)

    def __str__(self) -> str:
        currency = self.output_currency or self.currency
        return "%s%.2f" % (CurrencySymbols[currency], self.amount(currency, rounding=True))

    def __repr__(self) -> str:
        currency = self.output_currency or self.currency
        return "%s%s %.2f" % (
            (format_date(self.on_date) + " ") if self.on_date is not None else "",
            self.currency.value.upper(),
            self.amount(currency, rounding=True),
        )

    def __conform__(self, protocol: Any) -> Optional[str]:
        """Enables writing to an sqlite database

        https://docs.python.org/3/library/sqlite3.html#how-to-write-adaptable-objects

        Will also need the inverse (string to Money_*) to be registered with
        register_converter.
        """
        import sqlite3

        if protocol is sqlite3.PrepareProtocol:
            return repr(self)
        return None

    @classmethod
    def parse(cls, string: str) -> "BaseMoney":
        components = string.split(" ")
        if len(components) == 3:
            on_date, currency, amount = components
        elif len(components) == 2:
            currency, amount = components
            on_date = None
        else:
            raise RuntimeError("Cannot interpret string for parsing")

        return cls(amount, currency, on_date)


def Money(
    base_currency: Union[Currency, str],
    base_date: Optional[Union[date, str]] = None,
    output_currency: Optional[Union[Currency, str]] = None,
    class_name: Optional[str] = "",
) -> Type[BaseMoney]:
    """Factory that creates a class for computing with a currency on a date."""
    c_name = class_name or "Money_" + (
        format_date(base_date) if base_date is not None else "current"
    )
    class_attrs = {
        "base_date": parse_optional_date(base_date),
        "base_currency": base_currency,
        "output_currency": to_currency_enum(output_currency) if output_currency else None,
    }
    return type(c_name, (BaseMoney,), class_attrs)
