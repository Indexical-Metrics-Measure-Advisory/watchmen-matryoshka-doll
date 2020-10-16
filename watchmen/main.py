###
# 1. select basic domain for example insurance product ,marketing
# 2. read json from connector
# 3. generate basic lake base on json data
# 4. match lake with domain  knowledge dataset and provide suggestions
# 5. link knowledge domain to lake

from fastapi import FastAPI

# from watchmen.model.generate.model_schema_generater import generate_basic_schema
# from watchmen.model.model_schema import ModelSchema

app = FastAPI()


@app.get("/health")
async def health():
    return {"health": True}


# @app.get("/generate/{key}/{path}", response_model=ModelSchema)
# async def generate_schema(key: str, path: str):
#     return generate_basic_schema(key, path)








