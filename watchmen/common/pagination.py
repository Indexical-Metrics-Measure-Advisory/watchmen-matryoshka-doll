from pydantic import BaseModel


class Pagination(BaseModel):
     pageSize:int =None
     pageNumber:int = None
