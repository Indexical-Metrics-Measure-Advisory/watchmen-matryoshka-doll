import arrow


def __mask_day(date_str):
    return date_str[:8] + "**"


def __mask_month(date_str):
    return date_str[:5] + "**" + date_str[7:]


def encrypt_day(value_, params=None):
    date = arrow.get(value_)
    date_str = date.format('YYYY-MM-DD')
    return __mask_day(date_str)


def encrypt_month(value_, params=None):
    date = arrow.get(value_)
    date_str = date.format('YYYY-MM-DD')
    return __mask_month(date_str)


def encrypt_month_day(value_, params=None):
    date = arrow.get(value_)
    date_str = date.format('YYYY-MM-DD')
    return __mask_day(__mask_month(date_str))
