# -*- coding: utf-8 -*-

from typing import Tuple, Union, Optional, ClassVar, Dict, Any, Type

from decimal import Decimal, ROUND_HALF_UP

from dmon.currency import Currency, CurrencySymbols, to_currency_enum
from dmon.rates import get_rates, today


Numeric = Union[int, float, Decimal]


class BaseMoney:
    default_date: ClassVar[str] = today()
    default_currency: ClassVar[Currency] = Currency.EUR
    output_currency: Optional[Currency] = None

    # Precision for checking equality, applied to the cents. A 0 is
    # equivalent to rounding cents.
    precision: ClassVar[int] = 0

    def __init__(
        self,
        amount: Union[Numeric, Tuple[Numeric, Currency]],
        currency: Optional[Union[str, Currency]] = None,
        on: Optional[str] = None,
        amount_is_cents: bool = False,
    ) -> None:
        """
        Initializes a new instance of the BaseMoney class, intended to be used by derived clases.

        Args:
            amount (Union[Numeric, Tuple[Numeric, Currency]]): The amount of money.
                It can be a single numeric value or a tuple containing the amount and currency.
            currency (Optional[Union[str, Currency]]): The currency of the money.
                If not provided, the default currency of the class is used.
            on (Optional[str]): The date for which the money is represented.
                If not provided, the default date of the class is used.
            amount_is_cents (bool): A flag indicating whether the provided amount is in cents.
                If False (default), the amount is treated as the main currency unit (e.g., dollars).

        Attributes:
            _cents (Decimal): The amount of money stored as cents.
            currency (Currency): The currency of the money.
            on_date (str): The date for which the money is represented.
        """
        if isinstance(amount, tuple):
            amount, currency = amount

        self._cents: Decimal = (
            Decimal(amount) if amount_is_cents else Decimal('100') * Decimal(amount)
        )
        self.currency: Currency = to_currency_enum(currency or self.default_currency)
        self.on_date: str = on or self.default_date

    @classmethod
    def to_date(cls, dt: str) -> None:
        cls.default_date = dt

    @classmethod
    def to_today(cls) -> None:
        cls.to_date(today())

    def as_tuple(self) -> Tuple[Decimal, str]:
        return self._cents, self.currency.value

    def cents(
        self, currency: Optional[Union[str, Currency]] = None, on_date: Optional[str] = None
    ) -> Decimal:
        """Converts the money amount to cents in the specified
        currency on the given date.

        Args:

            currency: The target currency to convert to.  If not
                provided, the money's original currency is used.

            on_date: The date for which the conversion rates should be
                used.  If not provided, the money's original date is
                used.

        Returns:

            The amount in cents in the specified currency on the given
            date.

        Raises:

            RuntimeError: If the conversion rates are not available
            for the specified date.

        The function first converts the provided currency (if any) to
        a Currency enum.  If the target currency is the same as the
        money's original currency, the amount in cents is returned
        directly.

        The amount is then converted to cents in the target currency
        by multiplying it with the ratio of the target currency rate
        to the original currency rate.

        """
        currency = to_currency_enum(currency or self.currency)
        if currency == self.currency:
            return self._cents

        rates = get_rates(on_date or self.on_date, currency, self.currency)

        if rates is None:
            raise RuntimeError('Could not find rates for {on_date or self.on_date}')

        if rates[currency] is None:
            raise RuntimeError('Could not find conversion rate for ', currency)

        if rates[self.currency] is None:
            raise RuntimeError('Could not find conversion rate for ', self.currency)

        return self._cents * Decimal(str(rates[currency])) / Decimal(str(rates[self.currency]))

    def amount(
        self, currency: Optional[Union[str, Currency]] = None, rounding: bool = False
    ) -> Decimal:
        val = self.cents(currency)
        return (Decimal(round(val)) if rounding else val) / Decimal('100')

    def to(self, currency: Union[str, Currency]) -> 'BaseMoney':
        currency = to_currency_enum(currency)
        return self.__class__(
            self.cents(currency),
            currency,
            on=self.on_date,
            amount_is_cents=True,
        )

    def on(self, on_date: str) -> 'BaseMoney':
        return self.__class__(
            self._cents,
            self.currency,
            on=on_date,
            amount_is_cents=True,
        )

    def normalized_amounts(self, o: 'BaseMoney') -> Tuple[Decimal, Decimal, Currency, str]:
        """Returns the two values with which to operate, their common
        currency, and the date on which any conversion has
        happened. If the two currencies are the same we do not need to
        do any conversions; if they are not, they will both be
        converted to the default currency. The conversion date is the
        most recent one.
        """
        on_date = max(self.on_date, o.on_date)
        if self.currency == o.currency:
            return (self.cents(), o.cents(), self.currency, on_date)

        return (
            self.cents(self.default_currency, on_date=on_date),
            o.cents(self.default_currency, on_date=on_date),
            self.default_currency,
            on_date,
        )

    def __str__(self) -> str:
        currency = self.output_currency or self.currency
        return '%s%.2f' % (CurrencySymbols[currency], self.amount(currency, rounding=True))

    def __repr__(self) -> str:
        return str(self)

    def __neg__(self) -> 'BaseMoney':
        return self.__class__(-self._cents, self.currency, on=self.on_date, amount_is_cents=True)

    def __add__(self, o: Union['BaseMoney', Numeric]) -> 'BaseMoney':
        if not isinstance(o, BaseMoney):
            o = self.__class__(Decimal(o), self.currency)

        v1, v2, out_currency, on_date = self.normalized_amounts(o)
        return self.__class__(v1 + v2, out_currency, on=on_date, amount_is_cents=True)

    def __radd__(self, o: Union['BaseMoney', Numeric]) -> 'BaseMoney':
        return self + o

    def __sub__(self, o: 'BaseMoney') -> 'BaseMoney':
        v1, v2, out_currency, on_date = self.normalized_amounts(o)
        return self.__class__(v1 - v2, out_currency, on=on_date, amount_is_cents=True)

    def __rsub__(self, o: 'BaseMoney') -> 'BaseMoney':
        return -self + o

    def __mul__(self, n: Numeric) -> 'BaseMoney':
        return self.__class__(
            self._cents * Decimal(n), self.currency, on=self.on_date, amount_is_cents=True
        )

    __rmul__ = __mul__

    def __truediv__(self, n: Union['BaseMoney', Numeric]) -> Union['BaseMoney', Decimal]:
        if isinstance(n, BaseMoney):
            return self._cents / n.to(self.currency).cents()
        return self.__class__(
            self._cents / Decimal(n), self.currency, on=self.on_date, amount_is_cents=True
        )

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, BaseMoney):
            return NotImplemented
        v1, v2, _, _ = self.normalized_amounts(o)
        precision_decimal = Decimal('1').scaleb(-self.precision)
        v1_quantized = v1.quantize(precision_decimal, rounding=ROUND_HALF_UP)
        v2_quantized = v2.quantize(precision_decimal, rounding=ROUND_HALF_UP)
        return v1_quantized == v2_quantized

    def __ne__(self, o: object) -> bool:
        eq_result = self.__eq__(o)
        if eq_result is NotImplemented:
            return NotImplemented
        return not eq_result

    def __gt__(self, o: 'BaseMoney') -> bool:
        v1, v2, _, _ = self.normalized_amounts(o)
        return v1 > v2

    def __ge__(self, o: 'BaseMoney') -> bool:
        eq_result = self.__eq__(o)
        if eq_result is NotImplemented:
            return NotImplemented
        return eq_result or self.__gt__(o)

    def __lt__(self, o: 'BaseMoney') -> bool:
        v1, v2, _, _ = self.normalized_amounts(o)
        return v1 < v2

    def __le__(self, o: 'BaseMoney') -> bool:
        eq_result = self.__eq__(o)
        if eq_result is NotImplemented:
            return NotImplemented
        return eq_result or self.__lt__(o)

    def __conform__(self, protocol: Any) -> Optional[str]:
        """Enables writing to an sqlite database

        https://docs.python.org/3/library/sqlite3.html#how-to-write-adaptable-objects

        Will also need the inverse (string to Money_*) to be registered with
        register_converter.
        """
        import sqlite3

        if protocol is sqlite3.PrepareProtocol:
            amount, currency = self.as_tuple()
            return f"{str(amount)};{currency}"
        return None


def Money(
    currency: Union[str, Currency],
    output_currency: Optional[Union[str, Currency]] = None,
    on: Optional[str] = None,
    name: Optional[str] = '',
) -> Type[BaseMoney]:
    """Factory that creates a class for computing with a currency on a date."""
    class_name = name or 'Money_' + (on if on else 'latest')
    class_attrs = {
        'default_date': on or today(),
        'default_currency': currency,
        'output_currency': to_currency_enum(output_currency) if output_currency else None,
    }
    return type(class_name, (BaseMoney,), class_attrs)
