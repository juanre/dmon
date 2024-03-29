from typing import Union
from enum import Enum


class Currency(Enum):
    AED = 'aed'
    AFN = 'afn'
    ALL = 'all'
    AMD = 'amd'
    ANG = 'ang'
    ARS = 'ars'
    AUD = 'aud'
    AOA = 'aoa'
    AWG = 'awg'
    AZN = 'azn'
    BAM = 'bam'
    BBD = 'bbd'
    BDT = 'bdt'
    BGN = 'bgn'
    BIF = 'bif'
    BMD = 'bmd'
    BND = 'bnd'
    BOB = 'bob'
    BRL = 'brl'
    BSD = 'bsd'
    BWP = 'bwp'
    BZD = 'bzd'
    CAD = 'cad'
    CDF = 'cdf'
    CHF = 'chf'
    CLP = 'clp'
    CNY = 'cny'
    COP = 'cop'
    CRC = 'crc'
    CUP = 'cup'
    CZK = 'czk'
    CVE = 'cve'
    DJF = 'djf'
    DKK = 'dkk'
    DOP = 'dop'
    DZD = 'dzd'
    EGP = 'egp'
    ETB = 'etb'
    EUR = 'eur'
    FJD = 'fjd'
    FKP = 'fkp'
    GBP = 'gbp'
    GEL = 'gel'
    GGP = 'ggp'
    GIP = 'gip'
    GNF = 'gnf'
    GTQ = 'gtq'
    GYD = 'gyd'
    GMD = 'gmd'
    HKD = 'hkd'
    HNL = 'hnl'
    HRK = 'hrk'
    HTG = 'htg'
    HUF = 'huf'
    IDR = 'idr'
    ILS = 'ils'
    IMP = 'imp'
    INR = 'inr'
    IRR = 'irr'
    ISK = 'isk'
    JEP = 'jep'
    JMD = 'jmd'
    JPY = 'jpy'
    KES = 'kes'
    KGS = 'kgs'
    KHR = 'khr'
    KMF = 'kmf'
    KRW = 'krw'
    KYD = 'kyd'
    KZT = 'kzt'
    LAK = 'lak'
    LBP = 'lbp'
    LKR = 'lkr'
    LRD = 'lrd'
    LSL = 'lsl'
    MAD = 'mad'
    MDL = 'mdl'
    MGA = 'mga'
    MKD = 'mkd'
    MMK = 'mmk'
    MNT = 'mnt'
    MUR = 'mur'
    MXN = 'mxn'
    MYR = 'myr'
    MZN = 'mzn'
    MOP = 'mop'
    MVR = 'mvr'
    MWK = 'mwk'
    NAD = 'nad'
    NGN = 'ngn'
    NIO = 'nio'
    NOK = 'nok'
    NPR = 'npr'
    NZD = 'nzd'
    OMR = 'omr'
    PAB = 'pab'
    PEN = 'pen'
    PHP = 'php'
    PGK = 'pgk'
    PKR = 'pkr'
    PLN = 'pln'
    PYG = 'pyg'
    QAR = 'qar'
    RON = 'ron'
    RSD = 'rsd'
    RUB = 'rub'
    RWF = 'rwf'
    SAR = 'sar'
    SBD = 'sbd'
    SCR = 'scr'
    SEK = 'sek'
    SGD = 'sgd'
    SHP = 'shp'
    SLL = 'sll'
    SOS = 'sos'
    SRD = 'srd'
    SYP = 'syp'
    SZL = 'szl'
    THB = 'thb'
    TJS = 'tjs'
    TOP = 'top'
    TRY = 'try'
    TTD = 'ttd'
    TVD = 'tvd'
    TWD = 'twd'
    TZS = 'tzs'
    UAH = 'uah'
    UGX = 'ugx'
    USD = 'usd'
    UYU = 'uyu'
    UZS = 'uzs'
    VEF = 'vef'
    VND = 'vnd'
    VUV = 'vuv'
    WST = 'wst'
    XAF = 'xaf'
    XCD = 'xcd'
    XOF = 'xof'
    XPF = 'xpf'
    YER = 'yer'
    ZAR = 'zar'


CurrencySymbols = {
    Currency.AED: 'د.إ',
    Currency.AFN: '؋',
    Currency.ALL: 'Lek ',
    Currency.AMD: '֏',
    Currency.ANG: 'ƒ',
    Currency.ARS: 'AR$',
    Currency.AUD: 'A$',
    Currency.AOA: 'Kz ',
    Currency.AWG: 'ƒ',
    Currency.AZN: 'ман',
    Currency.BAM: 'KM ',
    Currency.BBD: 'BBD$',
    Currency.BDT: '৳',
    Currency.BGN: 'лв',
    Currency.BIF: 'FBu',
    Currency.BMD: '$',
    Currency.BND: 'B$',
    Currency.BOB: '$b',
    Currency.BRL: 'R$',
    Currency.BSD: 'B$',
    Currency.BWP: 'P ',
    Currency.BZD: 'BZ$',
    Currency.CAD: 'C$',
    Currency.CDF: 'FC ',
    Currency.CHF: 'CHF ',
    Currency.CLP: 'CLP',
    Currency.CNY: '¥',
    Currency.COP: 'COP',
    Currency.CRC: '₡',
    Currency.CUP: '₱',
    Currency.CZK: 'Kč',
    Currency.CVE: 'Esc ',
    Currency.DJF: 'Fdj',
    Currency.DKK: 'kr ',
    Currency.DOP: 'RD$',
    Currency.DZD: 'دج',
    Currency.EGP: 'E£',
    Currency.ETB: 'ብር',
    Currency.EUR: '€',
    Currency.FJD: 'FJ$',
    Currency.FKP: 'FK£',
    Currency.GBP: '£',
    Currency.GEL: 'ლ',
    Currency.GGP: 'G£',
    Currency.GIP: '£',
    Currency.GNF: 'GFr',
    Currency.GTQ: 'Q ',
    Currency.GYD: 'G$',
    Currency.GMD: 'D ',
    Currency.HKD: 'HK$',
    Currency.HNL: 'L ',
    Currency.HRK: 'kn ',
    Currency.HTG: 'G ',
    Currency.HUF: 'Ft ',
    Currency.IDR: 'Rp ',
    Currency.ILS: '₪',
    Currency.IMP: '£',
    Currency.INR: '₹',
    Currency.IRR: '﷼',
    Currency.ISK: 'kr ',
    Currency.JEP: '£',
    Currency.JMD: 'J$',
    Currency.JPY: 'JP¥',
    Currency.KES: 'Ksh ',
    Currency.KGS: 'лв',
    Currency.KHR: '៛',
    Currency.KMF: 'CF',
    Currency.KRW: '₩',
    Currency.KYD: 'CI$',
    Currency.KZT: 'лв',
    Currency.LAK: '₭',
    Currency.LBP: 'ل.ل.',
    Currency.LKR: '₨',
    Currency.LRD: 'L$',
    Currency.LSL: 'M ',
    Currency.MAD: 'MAD ',
    Currency.MDL: 'L ',
    Currency.MGA: 'Ar ',
    Currency.MKD: 'ден',
    Currency.MMK: 'K',
    Currency.MNT: '₮',
    Currency.MUR: '₨',
    Currency.MXN: 'Mex$',
    Currency.MYR: 'RM ',
    Currency.MZN: 'MT ',
    Currency.MOP: 'MOP$',
    Currency.MVR: 'Rf. ',
    Currency.MWK: 'MK ',
    Currency.NAD: 'N$',
    Currency.NGN: '₦',
    Currency.NIO: 'C$',
    Currency.NOK: 'kr ',
    Currency.NPR: '₨',
    Currency.NZD: 'NZ$',
    Currency.OMR: '﷼',
    Currency.PAB: 'B/.',
    Currency.PEN: 'S/.',
    Currency.PHP: '₱',
    Currency.PGK: 'K',
    Currency.PKR: '₨',
    Currency.PLN: 'zł',
    Currency.PYG: 'Gs ',
    Currency.QAR: '﷼',
    Currency.RON: 'lei ',
    Currency.RSD: 'Дин.',
    Currency.RUB: '₽',
    Currency.RWF: 'R₣',
    Currency.SAR: '﷼',
    Currency.SBD: 'SI$',
    Currency.SCR: '₨',
    Currency.SEK: 'kr ',
    Currency.SGD: 'S$',
    Currency.SHP: '£',
    Currency.SLL: 'Le ',
    Currency.SOS: 'S ',
    Currency.SRD: 'Sr$',
    Currency.SYP: '£S',
    Currency.SZL: 'L',
    Currency.THB: '฿',
    Currency.TJS: 'SM ',
    Currency.TOP: 'T$',
    Currency.TRY: '₤',
    Currency.TTD: 'TT$',
    Currency.TVD: '$T',
    Currency.TWD: 'NT$',
    Currency.TZS: 'TSh ',
    Currency.UAH: '₴',
    Currency.UGX: 'USh ',
    Currency.USD: '$',
    Currency.UYU: '$U ',
    Currency.UZS: 'лв',
    Currency.VEF: 'Bs ',
    Currency.VND: '₫',
    Currency.VUV: 'VT ',
    Currency.WST: 'WS$',
    Currency.XAF: 'FCFA ',
    Currency.XCD: 'EC$',
    Currency.XOF: 'CFA ',
    Currency.XPF: '₣',
    Currency.YER: '﷼',
    Currency.ZAR: 'R ',
}


Reverse_symbols = {v: k for k, v in CurrencySymbols.items()}

# These can be used in several currencies, choose one:
Reverse_symbols['C$'] = Currency.CAD
Reverse_symbols['A$'] = Currency.AUD
Reverse_symbols['$'] = Currency.USD
Reverse_symbols['£'] = Currency.GBP


def to_currency_enum(currency: Union[str, Currency]) -> Currency:
    if isinstance(currency, Currency):
        return currency
    return Currency(Reverse_symbols.get(currency, currency.lower()))
