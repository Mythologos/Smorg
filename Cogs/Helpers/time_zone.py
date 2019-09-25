from aenum import Enum


# note: names dictate military time zone name, if it exists
# continue here: https://www.timeanddate.com/time/zones/ ... at G
class TimeZone(Enum, init='value aliases'):
    A = (1, ('UTC+1', 'GMT+1', 'CET', 'WAT', 'BST', 'BST+1', 'BDT', 'BDST', 'IST', 'WEDT', 'WEST',
             'MEZ', 'ECT', 'ECT+1'))
    B = (2, ('UTC+2', 'GMT+2', 'EET', 'USZ1', 'CEDT', 'CEST', 'MEST', 'MESZ', 'CAT', 'ECST', 'OEZ'))
    C = (3, ('UTC+3', 'GMT+3', 'MSK', 'EAT', 'EEDT', 'EEST', 'AST', 'AST+3', 'OESZ', 'FET'))
    D = (4, ('UTC+4', 'GMT+4', 'SMT', 'AMT', 'AMT+4', 'AZT', 'GET', 'MUT', 'ADT', 'ADT+4'))
    E = (5, ('UTC+5', 'GMT+5', 'PKT', 'YEKT', 'MVT', 'AMST', 'AMST+5', 'AQTT', 'AZST'))
    F = (6, ('UTC+6', 'GMT+6', 'OMSK', 'BST', 'BST+6', 'ALMT', 'BTT'))
    G = (7, ('UTC+7', 'GMT+7', 'CXT', 'KRAT', 'DAVT'))
    H = (8, ('UTC+8', 'GMT+8', 'CST', 'CST+8', 'IRKT', 'AWST', 'WST', 'WADT', 'BNT', 'CAST',
             'CHOT'))
    I = (9, ('UTC+9', 'GMT+9', 'JST', 'YAKT', 'AWDT', 'CHOST'))
    K = (10, ('UTC+10', 'GMT+10', 'EAST', 'EAST+10', 'EST', 'EST+10', 'VLAT', 'AEST', 'AET', 'AET+10',
              'CHUT', 'ChST', 'GST', 'DDUT'))
    L = (11, ('UTC+11', 'GMT+11', 'SAKT', 'EADT', 'EST', 'EST+11', 'AEDT', 'AET', 'AET+11', 'BST',
              'BST+11'))
    M = (12, ('UTC+12', 'GMT+12', 'IDLE', 'NZST', 'NZT', 'MAGT', 'ANAST', 'ANAT', 'FJT'))
    MSTAR = (13, ('UTC+13', 'GMT+13', 'NZDT', 'FJST'))
    EXTRA = (14, ('UTC+14', ))
    N = (-1, ('UTC-1', 'GMT-1', 'WAT', 'AZOT', 'CVT', 'EGT'))
    O = (-2, ('UTC-2', 'GMT-2', 'AT', 'BRST', 'FNT'))
    P = (-3, ('UTC-3', 'GMT-3', 'ART', 'ADT', 'ADT-3', 'HAA', 'AMST', 'AMST-3', 'AT', 'AT-3', 'BRT',
              'CLST', 'CLST-3', 'CLDT', 'FKST'))
    Q = (-4, ('UTC-4', 'GMT-4', 'AST', 'AST-4', 'EDT', 'EDST', 'HAE', 'HNA', 'AMT', 'AMT-4', 'AT',
              'AT-4', 'BOT', 'CDT', 'CDT-4', 'CIDST', 'CLT', 'CT', 'CT-4', 'CLST', 'CLST-4',
              'NAEDT', 'FKT'))
    R = (-5, ('UTC-5', 'GMT-5', 'EST', 'EST-5', 'CDT', 'CDT-5', 'CDST', 'NACDT', 'HAC', 'HNE', 'ACT',
              'CIST', 'CIT', 'COT', 'CST', 'CST-5', 'CT', 'CT-5', 'EASST', 'ECT', 'ECT-5',
              'ET', 'NAEST'))
    S = (-6, ('UTC-6', 'GMT-6', 'CST', 'CST-6', 'CT', 'CT-6', 'NACST' 'MDT', 'HAR', 'HNC', 'EAST',
              'EAST+10'))
    T = (-7, ('UTC-7', 'GMT-7', 'MST', 'PDT', 'HAP', 'HNR'))
    U = (-8, ('UTC-8', 'GMT-8', 'PST', 'AKDT', 'YDT', 'HADT', 'HAY', 'HNP'))
    V = (-9, ('UTC-9', 'GMT-9', 'AKST', 'YMT', 'HDT', 'HNY'))
    W = (-10, ('UTC-10', 'GMT-10', 'HST', 'HAST', 'AHST', 'CAT', 'CKT'))
    X = (-11, ('UTC-11', 'GMT-11', 'NT'))
    Y = (-12, ('UTC-12', 'GMT-12', 'IDLW', 'AoE'))
    Z = (0, ('UTC', 'UTC+0', 'GMT', 'GMT+0', 'AZOST', 'EGST'))

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
