
from watchmen.pipeline.stage.stage import PipelineStage
from watchmen.row_data.model_schema import Domain
from watchmen.service.generate_schema import generate_basic_schema, generate_basic_schema_for_list_data


class GenerateLakeSchema(PipelineStage):

    def __init__(self):
        self.name="GenerateLakeSchema"

    def run(self, input_param, context):
        if self.__check_input_param(input_param):
            data_list = input_param[0]
            name = input_param[1]
            output_param = generate_basic_schema_for_list_data(name, data_list, Domain.INSURANCE)
            return output_param

    def dependency(self):
        return "SaveToMongo"

    def __check_input_param(self, input_param):
        return True  # TODO check input



