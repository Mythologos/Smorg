"""
This module consists of various enumerations and groups of constants relating to time.
This mainly includes classes like TimeZone which delve into what aliases relate to each UTC timezone offset
and sets of aliases or constants.
"""

from __future__ import annotations

from aenum import Enum, NamedConstant
from typing import Union


class TimeZone(Enum, init='value aliases'):
    """
    This enumeration contains various objects that link time zone aliases to their UTC offsets.
    It also makes them comparable.

    The name of each item in the enumeration is based on the military abbreviation for each one.
    The EXTRA item is the exception to this, as I could not find its abbreviation.
    """
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

    def __lt__(self, other: Union[int, float, complex, TimeZone]) -> bool:
        if isinstance(other, int) or isinstance(other, float) or isinstance(other, complex):
            lt_bool = self.value < other
        else:
            lt_bool = self.value < other.value
        return lt_bool

    def __gt__(self, other: Union[int, float, complex, TimeZone]) -> bool:
        if isinstance(other, int) or isinstance(other, float) or isinstance(other, complex):
            gt_bool = self.value > other
        else:
            gt_bool = self.value > other.value
        return gt_bool

    def __ge__(self, other: Union[int, float, complex, TimeZone]) -> bool:
        if isinstance(other, int) or isinstance(other, float) or isinstance(other, complex):
            ge_bool = self.value >= other
        else:
            ge_bool = self.value >= other.value
        return ge_bool

    def __le__(self, other: Union[int, float, complex, TimeZone]) -> bool:
        if isinstance(other, int) or isinstance(other, float) or isinstance(other, complex):
            le_bool = self.value <= other
        else:
            le_bool = self.value <= other.value
        return le_bool

    def __eq__(self, other: Union[int, float, complex, TimeZone]) -> bool:
        if isinstance(other, int) or isinstance(other, float) or isinstance(other, complex):
            eq_bool = self.value == other
        else:
            eq_bool = self.value == other.value
        return eq_bool

    def __ne__(self, other: Union[int, float, complex, TimeZone]) -> bool:
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
        """
        This method gets the lowest value of a UTC time zone offset in the TimeZone enumeration.

        :return int: the lowest value of a UTC time zone offset in the TimeZone enumeration.
        """
        sorted_zones_by_enum = sorted(TimeZone.__members__.values(), key=lambda full_entry: full_entry.value)
        lowest_zone_value = sorted_zones_by_enum[0].value
        return lowest_zone_value

    @staticmethod
    def get_highest_zone_value() -> int:
        """
        This method gets the highest value of a UTC time zone offset in the TimeZone enumeration.

        :return int: the highest value of a UTC time zone offset in the TimeZone enumeration.
        """
        sorted_zones_by_enum = sorted(TimeZone.__members__.values(), key=lambda full_entry: full_entry.value)
        highest_zone_value = sorted_zones_by_enum[-1].value
        return highest_zone_value

    @classmethod
    def list_time_zones(cls) -> list:
        """
        This method composes and returns a complete list of TimeZone objects from this enumeration.

        :return list: a complete list of TimeZone objects.
        """
        time_zone_list: list = []
        for i in range(cls.get_lowest_zone_value(), cls.get_highest_zone_value() + 1):
            time_zone_list.append(TimeZone(i))
        return time_zone_list


class DateConstant(NamedConstant):
    """
    This class contains various constant values for dates that may be used in multiple locations.
    """
    FIRST_DAY_OF_MONTH = 1
    LEAP_YEAR_MODULO = 4


class TimeConstant(NamedConstant):
    """
    This class contains various constant values for times that may be used in multiple locations.
    """
    START_MINUTE = 0
    END_MINUTE = 59
    START_HOUR = 0
    START_MERIDIEM_HOUR = 1
    END_MERIDIEM_HOUR = 12
    END_HOUR = 23


class MonthAliases(NamedConstant):
    """
    This class tallies various accepted names or indicators for months in textual input.
    """
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


class MonthConstant(Enum, init='value number_of_days'):
    """
    This enumeration contains various constant values for times that may be used in multiple locations.
    It also lists of the number of days that each month has.
    Since it is different in a leap year, February is listed in two different ways (with two different names).
    """
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


class PeriodConstant:
    """
    This class contains various constant values for periods of the day that may be used in multiple locations.
    """
    SINE_MERIDIEM = 0  # "without a midday," referring to how there's no period separation in a twenty-four hour clock
    ANTE_MERIDIEM = 1
    POST_MERIDIEM = 2
