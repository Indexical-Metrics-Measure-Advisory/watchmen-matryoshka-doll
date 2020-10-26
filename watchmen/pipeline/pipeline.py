
from watchmen.pipeline.stage.generate_schema import GenerateLakeSchema
from watchmen.pipeline.stage.save_to_mongo import SaveToMongo
from watchmen.service.generate_schema import generate_basic_schema
from watchmen.service.import_data import import_row_data
from watchmen.storage.data_schema_storage import insert_data_schema, update_data_schema


def basic_schema(json,domain=None):
    schema = generate_basic_schema("policy", json, domain)
    data = schema.dict()
    result = insert_data_schema(data)
    return result.inserted_id


def update_schema(id, json,domain=None):
    schema = generate_basic_schema("policy",json,domain)
    data = schema.dict()
    return update_data_schema(id,data)


def import_data(json,schema):
    # print(type(model_schema_set))
    return import_row_data(json,schema,None)


def run_factors():
    pass


def process_factor_results():
    pass


    # generate import lake
    # generate data statistics
    # return data basic explore

def build_default_pipeline():
    pipeline = Pipeline()
    pipeline.add(SaveToMongo())
    pipeline.add(GenerateLakeSchema())
    return pipeline


class Pipeline(object):

    def __init__(self):
        self.stages = []

    def add(self,stage):
        self.stages.append(stage)

    def build(self,stage_list):
        self.stages  = stage_list

    def run(self,input_param,context):
        output_param = None
        context["status"] = []
        for stage in self.stages:
            if stage.dependency() is None or stage.dependency() in  context["status"]:
                output_param = stage.run(input_param, context)
                context["status"].append(stage.name)
                input_param = output_param
            else:
                print(stage.dependency()+"is Missing")

        print(context)
        return output_param





