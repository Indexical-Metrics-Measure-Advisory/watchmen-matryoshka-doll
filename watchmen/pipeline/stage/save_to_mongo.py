# from watchmen.pipeline.stage.stage import PipelineStage
# from watchmen.raw_data_back.lake_data_storage import batch_import_data
#
#
# class SaveToMongo(PipelineStage):
#
#     def __init__(self):
#         self.name="SaveToMongo"
#
#     def run(self, input_param, context):
#         if self.__check_input_param(input_param):
#             json_files = input_param[0]
#             name = input_param[1]
#             batch_import_data(json_files, name)
#             # context["output"] = input_param
#             return [json_files,name]
#
#     def __check_input_param(self, input_param):
#         return True  # TODO check input
