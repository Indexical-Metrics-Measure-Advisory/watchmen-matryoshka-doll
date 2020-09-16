from pydantic import BaseModel


class Scene(BaseModel):
    sceneId:str = None
    code:str = None
