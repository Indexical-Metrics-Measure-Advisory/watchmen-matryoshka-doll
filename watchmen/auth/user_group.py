from pydantic import BaseModel


class UserGroup(BaseModel):
    userGroupId: int
    name: str = None
    description: str = None
    userIds: list
    spaceIds: list
