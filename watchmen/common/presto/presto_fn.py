from pypika.terms import Function


class PrestoMonth(Function):
    def __init__(self, date_part, alias=None):
        super(PrestoMonth, self).__init__("MONTH", date_part, alias=alias)


class PrestoYear(Function):
    def __init__(self, date_part, alias=None):
        super(PrestoYear, self).__init__("YEAR", date_part, alias=alias)


class PrestoDay(Function):
    def __init__(self, date_part, alias=None):
        super(PrestoDay, self).__init__("DAY", date_part, alias=alias)


class PrestoWeek(Function):
    def __init__(self, date_part, alias=None):
        super(PrestoDay, self).__init__("WEEK", date_part, alias=alias)


class PrestoDayOfWeek(Function):
    def __init__(self, date_part, alias=None):
        super(PrestoDayOfWeek, self).__init__("DAY_OF_WEEK", date_part, alias=alias)


class PrestoQuarter(Function):
    def __init__(self, date_part, alias=None):
        super(PrestoQuarter, self).__init__("QUARTER", date_part, alias=alias)


class PrestoDayOfMonth(Function):
    def __init__(self, date_part, alias=None):
        super(PrestoDayOfMonth, self).__init__("DAY_OF_MONTH", date_part, alias=alias)
