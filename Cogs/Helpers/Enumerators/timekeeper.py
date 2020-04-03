from aenum import Enum, NamedConstant
from typing import Union


# note: enum names dictate military time zone name, if it exists
# sites used: https://www.timeanddate.com/time/zones/ and
# https://greenwichmeantime.com/time-zone/definition/
class TimeZone(Enum, init='value aliases'):
    A = 1, ("BST", "CET", "MET", "MEZ", "WAT", "WETDST")
    B = 2, ("BDST", "CEST", "CETDST", "EET", "IST", "MEST", "MESZ", "METDST", "SAST")
    C = 3, ("EAT", "EEST", "EETDST", "FET", "IDT", "MSK")
    D = 4, ("AMST", "AZST", "AZT", "GEST", "GET", "MSD", "MUT", "RET", "SCT", "VOLT")
    E = 5, ("MAWT", "MUST", "MVT", "PKT", "TFT", 'YEKT', "TJT", "TMT", "UZT", "YEKT")
    F = 6, ("ALMT", "BDT", "BTT", "IOT", "KGST", "KGT", "OMMST", "OMST", "PKST", "UZST", "XJT", "YEKST")
    G = 7, ("ALMST", "CXT", "DAVT", "ICT", "KRAST", "KRAT", "NOVST", "NOVT", "WAST")
    H = 8, ("AWST", "BNT", "BORT", "CCT", "HKT", "IRKT", "IRKST", "MYT", "PHT", "SGT", "ULAT", "WADT")
    I = 9, ("AWSST", "JAYT", "JST", "KST", "PWT", "ULAST", "WDT", "YAKT", "YAKST")
    K = 10, ("AEST", "CHUT", "DDUT", "KDT", "LIGT", "MPT", "PGT", "TRUT", "VLAST", "VLAT", "YAPT")
    L = 11, ("AEDT", "AESST", "KOST", "LHDT", "MAGST", "MAGT", "PONT", "VUT")
    M = 12, ("ANAST", "ANAT", "FJT", "GILT", "MHT", "NZST", "NZT", "PETST", "PETT", "TVT", "WAKT", "WFT")
    MSTAR = 13, ("FJST", "NZDT", "PHOT", "TKT", "TOT")
    EXTRA = 14, ("LINT",)
    N = -1, ("AZOT", "EGT", "FNST")
    O = -2, ("BRST", "FNT", "PMDT", "UYST", "WGST")
    P = -3, ("ARST", "ART", "ADT", "BRA", "BRT", "CLST", "CLT", "FKST", "FKT", "GFT", "PMST", "PYST", "UYT", "WGT")
    Q = -4, ("AMT", "AST", "BOT", "EDT", "GYT", "PYT", "VET")
    R = -5, ("ACT", "CDT", "COT", "EASST", "EAST", "EST", "PET")
    S = -6, ("CST", "GALT", "MDT")
    T = -7, ("MST", "PDT")
    U = -8, ("AKDT", "PST")
    V = -9, ("AKST", "GAMT")
    W = -10, ("CKT", "HST", "TAHT")
    X = -11, ("NUT",)
    Y = -12, ()
    Z = 0, ("AZOST", "EGST", "GMT", "UCT", "UT", "UTC", "WET", "Z", "ZULU")

    def __lt__(self, other) -> bool:
        if isinstance(other, int) or isinstance(other, float) or isinstance(other, complex):
            lt_bool = self.value < other
        else:
            lt_bool = self.value < other.value
        return lt_bool

    def __gt__(self, other) -> bool:
        if isinstance(other, int) or isinstance(other, float) or isinstance(other, complex):
            gt_bool = self.value > other
        else:
            gt_bool = self.value > other.value
        return gt_bool

    def __ge__(self, other) -> bool:
        if isinstance(other, int) or isinstance(other, float) or isinstance(other, complex):
            ge_bool = self.value >= other
        else:
            ge_bool = self.value >= other.value
        return ge_bool

    def __le__(self, other) -> bool:
        if isinstance(other, int) or isinstance(other, float) or isinstance(other, complex):
            le_bool = self.value <= other
        else:
            le_bool = self.value <= other.value
        return le_bool

    def __eq__(self, other) -> bool:
        if isinstance(other, int) or isinstance(other, float) or isinstance(other, complex):
            eq_bool = self.value == other
        else:
            eq_bool = self.value == other.value
        return eq_bool

    def __ne__(self, other) -> bool:
        if isinstance(other, int) or isinstance(other, float) or isinstance(other, complex):
            ne_bool = self.value < other
        else:
            ne_bool = self.value < other.value
        return ne_bool

    def __str__(self) -> str:
        tz_template: str = f'Time Zone {self.name}: '
        for alias in self.aliases:
            tz_template.join(alias.join(', '))
        return tz_template.rstrip(', ').join('.')

    @staticmethod
    def get_lowest_zone_value() -> int:
        sorted_zones_by_enum = sorted(TimeZone.__members__.values(), key=lambda full_entry: full_entry.value)
        lowest_zone_value = sorted_zones_by_enum[0].value
        return lowest_zone_value

    @staticmethod
    def get_highest_zone_value() -> int:
        sorted_zones_by_enum = sorted(TimeZone.__members__.values(), key=lambda full_entry: full_entry.value)
        highest_zone_value = sorted_zones_by_enum[-1].value
        return highest_zone_value


class DateConstants(NamedConstant):
    FIRST_DAY_OF_MONTH = 1
    LEAP_YEAR_MODULO = 4


class TimeConstants(NamedConstant):
    START_MINUTE = 0
    END_MINUTE = 59
    START_HOUR = 0
    START_MERIDIEM_HOUR = 1
    END_MERIDIEM_HOUR = 12
    END_HOUR = 23


class MonthAliases(NamedConstant):
    JANUARY = ('January', 'Jan', '1')
    FEBRUARY = ('February', 'Feb', '2')
    MARCH = ('March', 'Mar', '3')
    APRIL = ('April', 'Apr', '4')
    MAY = ('May', '5')
    JUNE = ('June', 'Jun', '6')
    JULY = ('July', 'Jul', '7')
    AUGUST = ('August', 'Aug', '8')
    SEPTEMBER = ('September', 'Sept', '9')
    OCTOBER = ('October', 'Oct', '10')
    NOVEMBER = ('November', 'Nov', '11')
    DECEMBER = ('December', 'Dec', '12')


class MonthConstants(Enum, init='value number_of_days'):
    JANUARY = 1, 31
    FEBRUARY = 2, 28
    MARCH = 3, 31
    APRIL = 4, 30
    MAY = 5, 31
    JUNE = 6, 30
    JULY = 7, 31
    AUGUST = 8, 31
    SEPTEMBER = 9, 31
    OCTOBER = 10, 31
    NOVEMBER = 11, 30
    DECEMBER = 12, 31
    LEAP_YEAR_FEBRUARY = 13, 29


class PeriodConstants:
    SINE_MERIDIEM = 0  # "without a midday," referring to how there's no period separation in a twenty-four hour clock
    ANTE_MERIDIEM = 1
    POST_MERIDIEM = 2
