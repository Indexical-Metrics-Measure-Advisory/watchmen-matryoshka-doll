from model.model.pipeline.pipeline import Pipeline


def __process_mapping_actions(action):
    pass


def __process_factor_actions(action):
    pass


def __process_by_action_type(action):
    pass


async def build_pipeline_index_list(pipeline: Pipeline):
    for stage in pipeline.stages:
        for unit in stage.units:
            for action in unit.actions:
                results = __process_by_action_type(action)
                pass

    pass
