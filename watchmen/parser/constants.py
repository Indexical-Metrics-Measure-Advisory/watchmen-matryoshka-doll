from enum import Enum


class ParameterKind(str, Enum):
    TOPIC = "topic"
    CONSTANT = "constant"
    COMPUTED = "computed"


class ParameterValueType(str, Enum):
    SEQUENCE = 'sequence'
    NUMBER = 'number'
    UNSIGNED = 'unsigned'  # 0 & positive
    TEXT = 'text'

    # address
    ADDRESS = 'address',
    CONTINENT = 'continent',
    REGION = 'region',
    COUNTRY = 'country',
    PROVINCE = 'province',
    CITY = 'city',
    DISTRICT = 'district',
    ROAD = 'road',
    COMMUNITY = 'community',
    FLOOR = 'floor',
    RESIDENCE_TYPE = 'residence-type',
    RESIDENTIAL_AREA = 'residential-area',

    # contact electronic
    EMAIL = 'email',
    PHONE = 'phone',
    MOBILE = 'mobile',
    FAX = 'fax',

    # date time related
    DATETIME = 'datetime'  # YYYY - MM - DD HH: mm:ss
    FULL_DATETIME = 'full-datetime'  # YYYY - MM - DD HH: mm:ss.SSS
    DATE = 'date'  # YYYY - MM - DD
    TIME = 'time'  # HH: mm:ss
    YEAR = 'year'  # 4 digits
    HALF_YEAR = 'half-year'  # 1: first half, 2: second half
    QUARTER = 'quarter'  # 1 - 4
    MONTH = 'month'  # 1 - 12
    HALF_MONTH = 'half-month'  # 1: first half, 2: second half
    TEN_DAYS = 'ten-days'  # 1, 2, 3
    WEEK_OF_YEAR = 'week-of-year'  # 0(the partial week that precedes the first Sunday of the year) - 53(leap year)
    WEEK_OF_MONTH = 'week-of-month'  # 0(the partial week that precedes the first Sunday of the year) - 5
    HALF_WEEK = 'half-week'  # 1: first half, 2: second half
    DAY_OF_MONTH = 'day-of-month'  # 1 - 31, according to month / year
    DAY_OF_WEEK = 'day-of-week'  # 1(Sunday) - 7(Saturday)
    DAY_KIND = 'day-kind'  # 1: workday, 2: weekend, 3: holiday
    HOUR = 'hour'  # 0 - 23
    HOUR_KIND = 'hour-kind'  # 1: work time, 2: off hours, 3: sleeping time
    MINUTE = 'minute'  # 0 - 59
    SECOND = 'second'  # 0 - 59
    MILLISECOND = 'millisecond'  # 0 - 999
    AM_PM = 'am-pm'  # 1, 2

    # individual
    GENDER = 'gender'
    OCCUPATION = 'occupation'
    DATE_OF_BIRTH = 'date-of-birth'  # YYYY - MM - DD
    AGE = 'age'
    ID_NO = 'id-no'
    RELIGION = 'religion'
    NATIONALITY = 'nationality'

    # organization
    BIZ_TRADE = 'biz-trade'
    BIZ_SCALE = 'biz-scale'

    BOOLEAN = 'boolean'

    ENUM = 'enum'

    OBJECT = 'object'
    ARRAY = 'array'


class ComputedFunction(str, Enum):
    YEAR_OF = "year-of"
    MONTH_OF = "month-of"
    WEEK_OF_YEAR = "week-of-year"
    DAY_OF_WEEK = "day-of-week"
    WEEK_OF_MONTH = "week-of-month"
    QUARTER_OF = "quarter-of"
    HALF_YEAR_OF = "half-year-of"
    DAY_OF_MONTH = "day-of-month"


class ComputedCaseFunction(str, Enum):
    CASE_THEN = "case-then"


class Unit(str, Enum):
    YEAR = "year"
    MONTH = "month"
    DAY = "day"


class Function(str, Enum):
    YEAR_DIFF = "yearDiff"
    MONTH_DIFF = "monthDiff"
    DAY_DIFF = "dayDiff"


class Operator(str, Enum):
    ADD = "add"
    SUBTRACT = "subtract"
    MULTIPLY = "multiply"
    DIVIDE = "divide"
    MODULUS = "modulus"
