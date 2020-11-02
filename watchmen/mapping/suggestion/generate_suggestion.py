from watchmen.lake.model_schema_set import ModelSchemaSet
from watchmen.master.master_schema import MasterSchema
import spacy

nlp = spacy.load('en_core_web_sm')


def generate_topic_suggestion(lake_schema: ModelSchemaSet, master_space: MasterSchema):
    # generate topic match suggestion
    topic_match_results = []
    for topic in master_space.topic_list:
        topic_names = __build_topic_names(topic)
        master_topic_tokens = nlp(topic_names)
        for model_schema in lake_schema.schemas:
            model_name_tokens = nlp(model_schema.name)
            for master_token in master_topic_tokens:
                for model_token in model_name_tokens:
                    if master_token.has_vector:
                        similarity = master_token.similarity(model_token)
                        # if similarity > 0.7:
                        topic_match_results.append(
                            {"source": master_token.text, "target": model_token.text,
                             "similarity": str(similarity)})

    return topic_match_results


def __build_topic_names(topic):
    topic_name_list = [topic.businessKey]
    if topic.alias:
        topic_name_list.extend(topic.alias)
    topic_names = " ".join(topic_name_list)
    return topic_names


def generate_factor_suggestion(lake_schema: ModelSchemaSet, master_space: MasterSchema, topic_match_results: dict):
    for topic_match in topic_match_results:
        pass

    pass
