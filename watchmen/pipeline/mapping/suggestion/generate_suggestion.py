import decamelize
import spacy

from watchmen.raw_data_back.model_schema import ModelSchema
from watchmen.raw_data_back.model_schema_set import ModelSchemaSet
from watchmen.topic.topic import Topic

nlp = spacy.load('en_core_web_md')


def calculate_similarity(model_match_list):
    # print(model_match_list)
    similarity_list = list(map(lambda model_match: model_match["similarity"], model_match_list))
    similarity_sum = sum(similarity_list)
    return similarity_sum / len(similarity_list)


def generate_topic_suggestion(lake_schema: ModelSchemaSet, topic_list):
    # generate topic match suggestion
    topic_match_results = []
    for topic in topic_list:
        topic_names = __build_topic_names(topic)
        master_topic_tokens = nlp(topic_names)
        for key, model_schema in lake_schema.schemas.items():
            # print(model_schema)
            model_name_tokens = nlp(process_name(model_schema.name))
            model_match_list = []

            for master_token in master_topic_tokens:
                for model_token in model_name_tokens:
                    if master_token.has_vector:
                        similarity = master_token.similarity(model_token)
                        # if similarity > 0.6:
                        model_match_list.append(
                            {"source": master_token.text, "target": model_token.text,
                             "similarity": similarity})

            if model_match_list:
                similarity = calculate_similarity(model_match_list)
                topic_match_results.append({
                    "space": topic["topic_name"], "raw_data_back": model_schema.name, "similarity": similarity
                })

    return topic_match_results


def process_name(name):
    return decamelize.convert(name).replace("_", " ")


def __build_topic_names(topic):
    topic_name_list = [topic["topic_name"].replace("_", " ")]
    if topic["alias"]:
        topic_name_list.extend(topic["alias"])
    topic_names = " ".join(topic_name_list)
    return topic_names


def generate_factor_suggestion(lake_model: ModelSchema, topic: Topic):
    result_match_list = []
    for factor in topic["factors"]:
        factor_name = factor["factorName"]
        factor_tokens = nlp(process_name(factor_name))

        for key, field in lake_model.businessFields.items():
            field_matchs = []
            for factor_token in factor_tokens:
                field_tokens = nlp(process_name(key))
                for field_token in field_tokens:
                    if factor_token.has_vector:
                        similarity = factor_token.similarity(field_token)
                        field_matchs.append({
                            "factor": factor_token.text, "field": field_token.text, "similarity": similarity
                        })

            if field_matchs:

                similarity = calculate_similarity(field_matchs)
                if similarity > 0.6:
                    result_match_list.append({
                        "factor": factor_name, "lake_field": key, "similarity": similarity
                    })

    return result_match_list
