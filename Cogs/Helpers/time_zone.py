from aenum import Enum


# note: names dictate military time zone name
class TimeZone(Enum, init='value aliases'):
    A = (1, ('GMT+1', 'CET', 'WAT', 'BST', 'IST', 'WEDT', 'WEST', 'MEZ'))
    B = (2, ('GMT+2', 'EET', 'USZ1', 'CEDT', 'CEST', 'MEST', 'MESZ'))
    C = (3, ('GMT+3', 'MSK', 'EAT', 'EEDT', 'EEST'))
    D = (4, ('GMT+4', 'SMT', 'AMT', 'AZT', 'GET', 'MUT'))
    E = (5, ('GMT+5', 'PKT', 'YEKT', 'MVT'))
    F = (6, ('GMT+6', 'OMSK', 'BST'))
    G = (7, ('GMT+7', 'CXT', 'KRAT'))
    H = (8, ('GMT+8', 'CST', 'CST+8', 'IRKT', 'AWST', 'WST', 'WADT'))
    I = (9, ('GMT+9', 'JST', 'YAKT'))
    K = (10, ('GMT+10', 'EAST', 'EST', 'EST+10', 'VLAT'))
    L = (11, ('GMT+11', 'SAKT', 'EADT', 'EST', 'EST+11'))
    M = (12, ('GMT+12', 'IDLE', 'NZST', 'NZT', 'MAGT'))
    MSTAR = (13, ('GMT+13', 'NZDT'))
    N = (-1, ('GMT-1', 'WAT'))
    O = (-2, ('GMT-2', 'AT'))
    P = (-3, ('GMT-3', 'ART', 'ADT', 'HAA'))
    Q = (-4, ('GMT-4', 'AST', 'EDT', 'HAE', 'HNA'))
    R = (-5, ('GMT-5', 'EST', 'EST-5', 'CDT', 'HAC', 'HNE'))
    S = (-6, ('GMT-6', 'CST', 'CST-6', 'MDT', 'HAR', 'HNC'))
    T = (-7, ('GMT-7', 'MST', 'PDT', 'HAP', 'HNR'))
    U = (-8, ('GMT-8', 'PST', 'AKDT', 'YDT', 'HADT', 'HAY', 'HNP'))
    V = (-9, ('GMT-9', 'AKST', 'YMT', 'HDT', 'HNY'))
    W = (-10, ('GMT-10', 'HST', 'HAST', 'AHST', 'CAT'))
    X = (-11, ('GMT-11', 'NT'))
    Y = (-12, ('GMT-12', 'IDLW'))
    Z = (0, ('GMT', 'GMT-0', 'GMT+0'))

    def __lt__(self, other):
        if isinstance(other, int) or isinstance(other, float) or isinstance(other, complex):
            lt_bool = self.value < other
        else:
            lt_bool = self.value < other.value
        return lt_bool

    def __gt__(self, other):
        if isinstance(other, int) or isinstance(other, float) or isinstance(other, complex):
            gt_bool = self.value > other
        else:
            gt_bool = self.value > other.value
        return gt_bool

    def __ge__(self, other):
        if isinstance(other, int) or isinstance(other, float) or isinstance(other, complex):
            ge_bool = self.value >= other
        else:
            ge_bool = self.value >= other.value
        return ge_bool

    def __le__(self, other):
        if isinstance(other, int) or isinstance(other, float) or isinstance(other, complex):
            le_bool = self.value <= other
        else:
            le_bool = self.value <= other.value
        return le_bool

    def __eq__(self, other):
        if isinstance(other, int) or isinstance(other, float) or isinstance(other, complex):
            eq_bool = self.value == other
        else:
            eq_bool = self.value == other.value
        return eq_bool

    def __ne__(self, other):
        if isinstance(other, int) or isinstance(other, float) or isinstance(other, complex):
            ne_bool = self.value < other
        else:
            ne_bool = self.value < other.value
        return ne_bool

    def __str__(self):
        tz_template: str = 'Time Zone ' + self.name + ': '
        for alias in self.aliases:
            tz_template += alias + ', '
        tz_template = tz_template.rstrip(', ') + '.'
        return tz_template

    @staticmethod
    def get_lowest_zone_value():
        sorted_zones_by_enum = sorted(TimeZone.__members__.values(), key=lambda full_entry: full_entry.value)
        lowest_zone_value = sorted_zones_by_enum[0].value
        return lowest_zone_value

    @staticmethod
    def get_highest_zone_value():
        sorted_zones_by_enum = sorted(TimeZone.__members__.values(), key=lambda full_entry: full_entry.value)
        highest_zone_value = sorted_zones_by_enum[-1].value
        return highest_zone_value
