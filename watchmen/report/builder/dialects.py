from typing import Any

from pypika import Query
from pypika.queries import QueryBuilder


class PrestoQuery(Query):

    @classmethod
    def _builder(cls, **kwargs: Any) -> "PrestoQueryBuilder":
        return PrestoQueryBuilder(**kwargs)


class PrestoQueryBuilder(QueryBuilder):
    QUOTE_CHAR = None

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(dialect="presto", **kwargs)
