
from watchmen.pipeline.single.pipeline import build_pipeline, run_pipeline


def test_build_pipeline():
    stage_list = [{"name":"split_topic_by_schema","parameter":{"row_schema_name":"dasd"}},
                  {"name":"merge_to_topic","parameter":{"topic_name":"dasd"}}]

    # stage
    # tage("split_topic_by_schema", {"da", "da"})]  stage_list=[S
    pipeline =  build_pipeline(stage_list)

    run_pipeline(pipeline,{"topic_a":"dadas"})






