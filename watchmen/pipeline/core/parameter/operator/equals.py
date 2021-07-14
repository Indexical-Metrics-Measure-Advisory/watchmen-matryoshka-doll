import operator
from datetime import datetime, date
from decimal import Decimal

import arrow


def do_equals_with_value_type_check(left, right):
    # None
    if left is None and right is None:
        return True
    if left is None and isinstance(right, str):
        if right == "":
            return True
        else:
            return False
    if isinstance(left, str) and right is None:
        if left == "":
            return True
        else:
            return False
    # str
    if isinstance(left, str) and isinstance(right, str):
        return operator.eq(left, right)
    if isinstance(left, str) and (isinstance(right, int) or isinstance(right, Decimal)):
        return operator.eq(left, str(right))
    if isinstance(left, str) and (isinstance(right, datetime) or isinstance(right, date)):
        return operator.eq(left, arrow.get(right).format('YYYY-MM-DD'))
    if isinstance(left, str) and isinstance(right, dict):
        raise ValueError("operator equals, the left \"{0}\" is str, but the right \"{1}\" is dict".format(left, right))
    if isinstance(left, str) and isinstance(right, list):
        raise ValueError("operator equals, the left \"{0}\" is str, but the right \"{1}\" is list".format(left, right))

    # number,int, decimal
    if (isinstance(left, int) or isinstance(left, Decimal)) and isinstance(right, str):
        return operator.eq(str(left), right)
    if (isinstance(left, int) or isinstance(left, Decimal)) and (
            isinstance(right, int) or isinstance(right, Decimal)):
        return operator.eq(str(left), str(right))
    if (isinstance(left, int) or isinstance(left, Decimal)) and (
            isinstance(right, datetime) or isinstance(right, date)):
        raise ValueError(
            "operator equals, the left \"{0}\" is int or decimal, but the right \"{1}\" is datetime or date".format(
                left, right))
    if (isinstance(left, int) or isinstance(left, Decimal)) and isinstance(right, dict):
        raise ValueError(
            "operator equals, the left \"{0}\" is int or decimal, but the right \"{1}\" is dict".format(left, right))
    if (isinstance(left, int) or isinstance(left, Decimal)) and isinstance(right, list):
        raise ValueError(
            "operator equals, the left \"{0}\" is int or decimal, but the right \"{1}\" is list".format(left, right))

    # datetime and date
    if (isinstance(left, datetime) or isinstance(left, date)) and isinstance(right, str):
        return operator.eq(arrow.get(left).format('YYYY-MM-DD'), right)
    if (isinstance(left, datetime) or isinstance(left, date)) and (
            isinstance(right, int) or isinstance(right, Decimal)):
        raise ValueError(
            "operator equals, the left \"{0}\" is datetime or date, but the right \"{1}\" is int or decimal".format(
                left, right))
    if (isinstance(left, datetime) or isinstance(left, date)) and (
            isinstance(right, datetime) or isinstance(right, date)):
        return operator.eq(arrow.get(left).format('YYYY-MM-DD'), arrow.get(right).format('YYYY-MM-DD'))
    if (isinstance(left, datetime) or isinstance(left, date)) and isinstance(right, dict):
        raise ValueError(
            "operator equals, the left \"{0}\" is datetime or date, but the right \"{1}\" is dict".format(left, right))
    if (isinstance(left, datetime) or isinstance(left, date)) and isinstance(right, list):
        raise ValueError(
            "operator equals, the left \"{0}\" is datetime or date, but the right \"{1}\" is list".format(left, right))

    # dict
    if isinstance(left, dict) and isinstance(right, str):
        raise ValueError("operator equals, the left \"{0}\" is dict, but the right \"{1}\" is str".format(left, right))
    if isinstance(left, dict) and (isinstance(right, int) or isinstance(right, Decimal)):
        raise ValueError(
            "operator equals, the left \"{0}\" is dict, but the right \"{1}\" is int or decimal".format(left, right))
    if isinstance(left, dict) and (isinstance(right, datetime) or isinstance(right, date)):
        raise ValueError(
            "operator equals, the left \"{0}\" is dict, but the right \"{1}\" is datetime or date".format(left, right))
    if isinstance(left, dict) and isinstance(right, dict):
        return operator.eq(left, right)
    if isinstance(left, dict) and isinstance(right, list):
        raise ValueError("operator equals, the left \"{0}\" is dict, but the right \"{1}\" is list".format(left, right))

    # list
    if isinstance(left, list) and isinstance(right, str):
        raise ValueError("operator equals, the left \"{0}\" is list, but the right \"{1}\" is str".format(left, right))
    if isinstance(left, list) and (isinstance(right, int) or isinstance(right, Decimal)):
        raise ValueError(
            "operator equals, the left \"{0}\" is list, but the right \"{1}\" is int or decimal".format(left, right))
    if isinstance(left, list) and (isinstance(right, datetime) or isinstance(right, date)):
        raise ValueError(
            "operator equals, the left \"{0}\" is list, but the right \"{1}\" is datetime or date".format(left, right))
    if isinstance(left, list) and isinstance(right, dict):
        raise ValueError("operator equals, the left \"{0}\" is list, but the right \"{1}\" is dict".format(left, right))
    if isinstance(left, list) and isinstance(right, list):
        return operator.eq(left, right)

    return operator.eq(left, right)
