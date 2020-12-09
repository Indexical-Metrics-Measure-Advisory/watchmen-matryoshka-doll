from watchmen.pipeline.stage.stage import PipelineStage
from watchmen.row_data.storage.row_schema_storage import insert_data_schema


class SaveSchemaToMongo(PipelineStage):

    def __init__(self):
        self.name="SaveSchemaToMongo"

    def run(self, input_param, context):
        #TODO add link index
        insert_data_schema(input_param.dict())
        return input_param


    def dependency(self):
        return "GenerateLakeSchema"

