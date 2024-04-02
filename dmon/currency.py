from typing import Union
from enum import Enum


class Currency(Enum):
    AED = "aed"
    AFN = "afn"
    ALL = "all"
    AMD = "amd"
    ANG = "ang"
    ARS = "ars"
    AUD = "aud"
    AOA = "aoa"
    AWG = "awg"
    AZN = "azn"
    BAM = "bam"
    BBD = "bbd"
    BDT = "bdt"
    BGN = "bgn"
    BHD = "bhd"
    BIF = "bif"
    BMD = "bmd"
    BND = "bnd"
    BOB = "bob"
    BRL = "brl"
    BSD = "bsd"
    BTN = "btn"
    BWP = "bwp"
    BYN = "byn"
    BZD = "bzd"
    CAD = "cad"
    CDF = "cdf"
    CHF = "chf"
    CLP = "clp"
    CNY = "cny"
    COP = "cop"
    CRC = "crc"
    CUP = "cup"
    CZK = "czk"
    CVE = "cve"
    DJF = "djf"
    DKK = "dkk"
    DOP = "dop"
    DZD = "dzd"
    EGP = "egp"
    ERN = "ern"
    ETB = "etb"
    EUR = "eur"
    FJD = "fjd"
    FKP = "fkp"
    GBP = "gbp"
    GEL = "gel"
    GGP = "ggp"
    GHS = "ghs"
    GIP = "gip"
    GNF = "gnf"
    GTQ = "gtq"
    GYD = "gyd"
    GMD = "gmd"
    HKD = "hkd"
    HNL = "hnl"
    HRK = "hrk"
    HTG = "htg"
    HUF = "huf"
    IDR = "idr"
    ILS = "ils"
    IMP = "imp"
    INR = "inr"
    IQD = "iqd"
    IRR = "irr"
    ISK = "isk"
    JEP = "jep"
    JMD = "jmd"
    JOD = "jod"
    JPY = "jpy"
    KES = "kes"
    KGS = "kgs"
    KHR = "khr"
    KMF = "kmf"
    KPW = "kpw"
    KRW = "krw"
    KWD = "kwd"
    KYD = "kyd"
    KZT = "kzt"
    LAK = "lak"
    LBP = "lbp"
    LKR = "lkr"
    LRD = "lrd"
    LSL = "lsl"
    LYD = "lyd"
    MAD = "mad"
    MDL = "mdl"
    MGA = "mga"
    MKD = "mkd"
    MMK = "mmk"
    MNT = "mnt"
    MRU = "mru"
    MUR = "mur"
    MXN = "mxn"
    MYR = "myr"
    MZN = "mzn"
    MOP = "mop"
    MVR = "mvr"
    MWK = "mwk"
    NAD = "nad"
    NGN = "ngn"
    NIO = "nio"
    NOK = "nok"
    NPR = "npr"
    NZD = "nzd"
    OMR = "omr"
    PAB = "pab"
    PEN = "pen"
    PHP = "php"
    PGK = "pgk"
    PKR = "pkr"
    PLN = "pln"
    PYG = "pyg"
    QAR = "qar"
    RON = "ron"
    RSD = "rsd"
    RUB = "rub"
    RWF = "rwf"
    SAR = "sar"
    SBD = "sbd"
    SCR = "scr"
    SDG = "sdg"
    SEK = "sek"
    SGD = "sgd"
    SHP = "shp"
    SLE = "sle"
    SLL = "sll"
    SOS = "sos"
    SRD = "srd"
    SSP = "ssp"
    STD = "std"
    SYP = "syp"
    SZL = "szl"
    THB = "thb"
    TJS = "tjs"
    TMT = "tmt"
    TND = "tnd"
    TOP = "top"
    TRY = "try"
    TTD = "ttd"
    TVD = "tvd"
    TWD = "twd"
    TZS = "tzs"
    UAH = "uah"
    UGX = "ugx"
    USD = "usd"
    UYU = "uyu"
    UZS = "uzs"
    VEF = "vef"
    VES = "ves"
    VND = "vnd"
    VUV = "vuv"
    WST = "wst"
    XAF = "xaf"
    XCD = "xcd"
    XOF = "xof"
    XPF = "xpf"
    YER = "yer"
    ZAR = "zar"
    ZMW = "zmw"


CurrencySymbols = {
    Currency.AED: "د.إ",
    Currency.AFN: "؋",
    Currency.ALL: "Lek ",
    Currency.AMD: "֏",
    Currency.ANG: "ƒ",
    Currency.ARS: "AR$",
    Currency.AUD: "A$",
    Currency.AOA: "Kz ",
    Currency.AWG: "ƒ",
    Currency.AZN: "ман",
    Currency.BAM: "KM ",
    Currency.BBD: "BBD$",
    Currency.BDT: "৳",
    Currency.BGN: "лв",
    Currency.BHD: ".د.ب",
    Currency.BIF: "FBu",
    Currency.BMD: "$",
    Currency.BND: "B$",
    Currency.BOB: "$b",
    Currency.BRL: "R$",
    Currency.BSD: "B$",
    Currency.BTN: "Nu.",
    Currency.BWP: "P ",
    Currency.BYN: "Rbl‎",
    Currency.BZD: "BZ$",
    Currency.CAD: "C$",
    Currency.CDF: "FC ",
    Currency.CHF: "CHF ",
    Currency.CLP: "CLP",
    Currency.CNY: "¥",
    Currency.COP: "COP",
    Currency.CRC: "₡",
    Currency.CUP: "₱",
    Currency.CZK: "Kč",
    Currency.CVE: "Esc ",
    Currency.DJF: "Fdj",
    Currency.DKK: "kr ",
    Currency.DOP: "RD$",
    Currency.DZD: "دج",
    Currency.EGP: "E£",
    Currency.ERN: "Nkf‎",
    Currency.ETB: "ብር",
    Currency.EUR: "€",
    Currency.FJD: "FJ$",
    Currency.FKP: "FK£",
    Currency.GBP: "£",
    Currency.GEL: "ლ",
    Currency.GGP: "G£",
    Currency.GHS: "GH₵",
    Currency.GIP: "£",
    Currency.GNF: "GFr",
    Currency.GTQ: "Q ",
    Currency.GYD: "G$",
    Currency.GMD: "D ",
    Currency.HKD: "HK$",
    Currency.HNL: "L ",
    Currency.HRK: "kn ",
    Currency.HTG: "G ",
    Currency.HUF: "Ft ",
    Currency.IDR: "Rp ",
    Currency.ILS: "₪",
    Currency.IMP: "£",
    Currency.INR: "₹",
    Currency.IQD: "د.ع",
    Currency.IRR: "﷼",
    Currency.ISK: "kr ",
    Currency.JEP: "£",
    Currency.JMD: "J$",
    Currency.JOD: "د.أ",
    Currency.JPY: "JP¥",
    Currency.KES: "Ksh ",
    Currency.KGS: "лв",
    Currency.KHR: "៛",
    Currency.KMF: "CF",
    Currency.KPW: "₩",
    Currency.KRW: "₩",
    Currency.KWD: "د.ك",
    Currency.KYD: "CI$",
    Currency.KZT: "лв",
    Currency.LAK: "₭",
    Currency.LBP: "ل.ل.",
    Currency.LKR: "₨",
    Currency.LRD: "L$",
    Currency.LSL: "M ",
    Currency.LYD: "ل.د",
    Currency.MAD: "MAD ",
    Currency.MDL: "L ",
    Currency.MGA: "Ar ",
    Currency.MKD: "ден",
    Currency.MMK: "K",
    Currency.MNT: "₮",
    Currency.MRU: "UM‎",
    Currency.MUR: "₨",
    Currency.MXN: "Mex$",
    Currency.MYR: "RM ",
    Currency.MZN: "MT ",
    Currency.MOP: "MOP$",
    Currency.MVR: "Rf. ",
    Currency.MWK: "MK ",
    Currency.NAD: "N$",
    Currency.NGN: "₦",
    Currency.NIO: "C$",
    Currency.NOK: "kr ",
    Currency.NPR: "₨",
    Currency.NZD: "NZ$",
    Currency.OMR: "﷼",
    Currency.PAB: "B/.",
    Currency.PEN: "S/.",
    Currency.PHP: "₱",
    Currency.PGK: "K",
    Currency.PKR: "₨",
    Currency.PLN: "zł",
    Currency.PYG: "Gs ",
    Currency.QAR: "﷼",
    Currency.RON: "lei ",
    Currency.RSD: "Дин.",
    Currency.RUB: "₽",
    Currency.RWF: "R₣",
    Currency.SAR: "﷼",
    Currency.SBD: "SI$",
    Currency.SCR: "₨",
    Currency.SDG: "PT",
    Currency.SEK: "kr ",
    Currency.SGD: "S$",
    Currency.SHP: "£",
    Currency.SLE: "Le ",
    Currency.SLL: "Le ",
    Currency.SOS: "S ",
    Currency.SRD: "Sr$",
    Currency.SSP: "SS£",
    Currency.STD: "Db",
    Currency.SYP: "£S",
    Currency.SZL: "L",
    Currency.THB: "฿",
    Currency.TJS: "SM ",
    Currency.TMT: "m",
    Currency.TND: "د.ت‎",
    Currency.TOP: "T$",
    Currency.TRY: "₤",
    Currency.TTD: "TT$",
    Currency.TVD: "$T",
    Currency.TWD: "NT$",
    Currency.TZS: "TSh ",
    Currency.UAH: "₴",
    Currency.UGX: "USh ",
    Currency.USD: "$",
    Currency.UYU: "$U ",
    Currency.UZS: "лв",
    Currency.VEF: "Bs ",
    Currency.VES: "Bs. S",
    Currency.VND: "₫",
    Currency.VUV: "VT ",
    Currency.WST: "WS$",
    Currency.XAF: "FCFA ",
    Currency.XCD: "EC$",
    Currency.XOF: "CFA ",
    Currency.XPF: "₣",
    Currency.YER: "﷼",
    Currency.ZAR: "R ",
    Currency.ZMW: "ZK",
}


ReverseCurrencySymbols = {v: k for k, v in CurrencySymbols.items()}

# These can be used in several currencies, choose one:
ReverseCurrencySymbols["C$"] = Currency.CAD
ReverseCurrencySymbols["A$"] = Currency.AUD
ReverseCurrencySymbols["$"] = Currency.USD
ReverseCurrencySymbols["£"] = Currency.GBP


def to_currency_enum(currency: Union[str, Currency]) -> Currency:
    if isinstance(currency, Currency):
        return currency
    return Currency(ReverseCurrencySymbols.get(currency, currency.lower()))
