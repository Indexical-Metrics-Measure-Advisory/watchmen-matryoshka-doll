import operator
from datetime import datetime, date
from decimal import Decimal

import arrow
from arrow import ParserError


def do_less_with_value_type_check(left, right):
    # None
    if left is None or right is None:
        return False

    # str
    if isinstance(left, str) and isinstance(right, str):
        if left.isdigit() and right.isdigit():
            return operator.lt(Decimal(left), Decimal(right))
        else:
            raise TypeError(
                "operator less, the left \"{0}\" is str, the right \"{1}\" is str".format(
                    left, right))
    if isinstance(left, str) and (isinstance(right, int) or isinstance(right, Decimal)):
        return operator.lt(Decimal(left), right)
    if isinstance(left, str) and (isinstance(right, datetime) or isinstance(right, date)):
        try:
            return operator.lt(arrow.get(left).date(), arrow.get(right).date())
        except ParserError:
            raise TypeError(
                "operator less, the left \"{0}\" can not be match by date format, the right \"{1}\" is datetime or date".format(
                    left, right))
    if isinstance(left, str) and isinstance(right, dict):
        raise TypeError("operator less, the left \"{0}\" is str, the right \"{1}\" is dict".format(left, right))
    if isinstance(left, str) and isinstance(right, list):
        raise TypeError("operator less, the left \"{0}\" is str, the right \"{1}\" is list".format(left, right))

    # number, int, decimal
    if (isinstance(left, int) or isinstance(left, Decimal)) and isinstance(right, str):
        if right.isdigit():
            return operator.lt(Decimal(left), Decimal(right))
        else:
            raise TypeError(
                "operator less, the left \"{0}\" is int or decimal, the right \"{1}\" is str".format(left, right))
    if (isinstance(left, int) or isinstance(left, Decimal)) and (
            isinstance(right, int) or isinstance(right, Decimal)):
        return operator.lt(Decimal(left), Decimal(right))
    if (isinstance(left, int) or isinstance(left, Decimal)) and (
            isinstance(right, datetime) or isinstance(right, date)):
        try:
            return operator.lt(arrow.get(str(left)).date(), arrow.get(right).date())
        except ParserError:
            raise TypeError(
                "operator less, the left \"{0}\" can not be match by date format, the right \"{1}\" is datetime or date".format(
                    left, right))
    if (isinstance(left, int) or isinstance(left, Decimal)) and isinstance(right, dict):
        raise TypeError(
            "operator less, the left \"{0}\" is int or decimal, the right \"{1}\" is dict".format(left, right))
    if (isinstance(left, int) or isinstance(left, Decimal)) and isinstance(right, list):
        raise TypeError(
            "operator less, the left \"{0}\" is int or decimal, the right \"{1}\" is list".format(left, right))

    # datetime and date
    if (isinstance(left, datetime) or isinstance(left, date)) and isinstance(right, str):
        try:
            return operator.lt(arrow.get(left).date(), arrow.get(right).date())
        except ParserError:
            raise TypeError(
                "operator less, the left \"{0}\" is datetime or date, the right \"{1}\" is str, can not match date "
                "format".format(
                    left, right))
    if (isinstance(left, datetime) or isinstance(left, date)) and (
            isinstance(right, int) or isinstance(right, Decimal)):
        try:
            return operator.lt(arrow.get(left).date(), arrow.get(str(right)).date())
        except ParserError:
            raise TypeError(
                "operator less, the left \"{0}\" is datetime or date, the right \"{1}\" is int or decimal".format(
                    left, right))
    if (isinstance(left, datetime) or isinstance(left, date)) and (
            isinstance(right, datetime) or isinstance(right, date)):
        return operator.lt(arrow.get(left).date(), arrow.get(right).date())
    if (isinstance(left, datetime) or isinstance(left, date)) and isinstance(right, dict):
        raise TypeError(
            "operator less, the left \"{0}\" is datetime or date, but the right \"{1}\" is dict".format(left, right))
    if (isinstance(left, datetime) or isinstance(left, date)) and isinstance(right, list):
        raise TypeError(
            "operator less, the left \"{0}\" is datetime or date, but the right \"{1}\" is list".format(left, right))

    # dict
    if isinstance(left, dict) and isinstance(right, str):
        raise TypeError("operator less, the left \"{0}\" is dict, the right \"{1}\" is str".format(left, right))
    if isinstance(left, dict) and (isinstance(right, int) or isinstance(right, Decimal)):
        raise TypeError(
            "operator less, the left \"{0}\" is dict, the right \"{1}\" is int or decimal".format(left, right))
    if isinstance(left, dict) and (isinstance(right, datetime) or isinstance(right, date)):
        raise TypeError(
            "operator less, the left \"{0}\" is dict, the right \"{1}\" is datetime or date".format(left, right))
    if isinstance(left, dict) and isinstance(right, dict):
        raise TypeError("operator less, the left \"{0}\" is dict, the right \"{1}\" is dict".format(left, right))
    if isinstance(left, dict) and isinstance(right, list):
        raise TypeError("operator less, the left \"{0}\" is dict, the right \"{1}\" is list".format(left, right))

    # list
    if isinstance(left, list) and isinstance(right, str):
        raise TypeError("operator less, the left \"{0}\" is list, the right \"{1}\" is str".format(left, right))
    if isinstance(left, list) and (isinstance(right, int) or isinstance(right, Decimal)):
        raise TypeError(
            "operator less, the left \"{0}\" is list, the right \"{1}\" is int or decimal".format(left, right))
    if isinstance(left, list) and (isinstance(right, datetime) or isinstance(right, date)):
        raise TypeError(
            "operator less, the left \"{0}\" is list, the right \"{1}\" is datetime or date".format(left, right))
    if isinstance(left, list) and isinstance(right, dict):
        raise TypeError("operator less, the left \"{0}\" is list, the right \"{1}\" is dict".format(left, right))
    if isinstance(left, list) and isinstance(right, list):
        raise TypeError("operator less, the left \"{0}\" is list, the right \"{1}\" is list".format(left, right))

    return operator.lt(left, right)
