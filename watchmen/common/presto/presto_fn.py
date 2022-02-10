from pypika.terms import Function


class PrestoMonth(Function):
    def __init__(self, date_part, alias=None):
        # date_part = getattr(date_part, "value", date_part)
        super(PrestoMonth, self).__init__("MONTH", date_part, alias=alias)


class PrestoYear(Function):
    def __init__(self, date_part, alias=None):
        # date_part = getattr(date_part, "value", date_part)
        super(PrestoYear, self).__init__("YEAR", date_part, alias=alias)


class PrestoDay(Function):
    def __init__(self, date_part, alias=None):
        # date_part = getattr(date_part, "value", date_part)
        super(PrestoDay, self).__init__("DAY", date_part, alias=alias)

class PrestoDayOfWeek(Function):
    def __init__(self, date_part, alias=None):
        # date_part = getattr(date_part, "value", date_part)
        super(PrestoDay, self).__init__("DAY_OF_WEEK", date_part, alias=alias)


class PrestoDayOfYear(Function):
    def __init__(self, date_part, alias=None):
        # date_part = getattr(date_part, "value", date_part)
        super(PrestoDay, self).__init__("DAY_OF_YEAR", date_part, alias=alias)