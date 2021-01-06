from typing import List

from bson import ObjectId
from fastapi import HTTPException
from pydantic import BaseModel

# TODO replace mock service for user
from watchmen.auth.service.user import get_current_user, check_promise
from watchmen.auth.user import User
from watchmen.pipeline.mapping.suggestion.generate_suggestion import generate_topic_suggestion, \
    generate_factor_suggestion
from watchmen.pipeline.mapping.topic_mapping_rule import TopicMappingRule
from watchmen.common.knowledge.knowledge_loader import find_template_by_domain
from watchmen.raw_data.model_schema import ModelSchema

from watchmen.topic.factor.factor import Factor
from watchmen.space.index import create_space_by_domain_template, add_topic_list_to_master, get_summary_for_master_space, \
    add_topic_to_master_space, load_master_space
from watchmen.space.space import Space
from watchmen.pipeline.mapping.mapping_rule_storage import save_topic_mapping_rule, load_topic_mapping_by_name
from watchmen.topic.storage.topic_schema_storage import get_topic_list_by_ids

from watchmen.topic.topic import Topic


class SpaceOut(BaseModel):
    master_space: Space = None
    topic_list: List[Topic] = None


def auth_login(user: User):
    return True
    # pass


def auth_logout(user: User):
    return True
    # pass


# design time data integration
def select_domain(domain: str):
    current_user = get_current_user()
    if check_promise(current_user):
        # find domain template
        topic_list = find_template_by_domain(domain)
        # create space space
        master_space = create_space_by_domain_template(current_user, domain)
        # add template to space space
        master_space = add_topic_list_to_master(topic_list, master_space)
        # get summary for master_space
        return get_summary_for_master_space(master_space)
    else:
        raise HTTPException(status_code=401, detail="NO_PROMISE")

#
# def generate_raw_data_schema(json_files, name):
#     current_user = get_current_user()
#     if check_promise(current_user):
#         if use_default_pipeline(current_user):
#             pipeline = build_default_pipeline()
#             output_param = pipeline.run([json_files, name], {})
#             # print(output_param)
#             return output_param
#         else:
#             # load  customize_pipeline
#             pass
#             # TODO customize_pipeline run
#
#         # pass
#     else:
#         raise HTTPException(status_code=401, detail="NO_PROMISE")
#

# CRUD for pipeline



def generate_suggestion_topic_service(lake_schema, master_schema):
    topic_id_list = master_schema.topic_id_list
    object_ids = map(lambda x: ObjectId(x), topic_id_list)
    topic_list = get_topic_list_by_ids(list(object_ids))
    return generate_topic_suggestion(lake_schema, topic_list)


def generate_suggestion_factor(lake_model: ModelSchema, topic: Topic):
    return generate_factor_suggestion(lake_model, topic)


# def add_topic_mapping_rule():
#     pass


def check_factor_is_exist():
    # check same factor and return similarity factor
    pass


def load_topic_mapping(source_topic_name, target_topic_name):
    return load_topic_mapping_by_name(source_topic_name, target_topic_name)


def save_topic_mapping(topic_mapping_rule: TopicMappingRule):
    return save_topic_mapping_rule(topic_mapping_rule)


def load_space_topic_list(space_name) -> SpaceOut:
    master_space = load_master_space(space_name)
    topic_id_list = master_space.topic_id_list

    topic_list = get_topic_list_by_ids(topic_id_list)
    # master_space.topic_list = topic_list
    return SpaceOut(master_space, topic_list)

    # TODO user info missing


def add_factor_to_master_topic(factor: Factor, master_space):
    # current_user = get_current_user()

    pass


def add_topic_to_master(topic, master_space):
    return add_topic_to_master_space(topic, master_space)


# CRUD for space schema and relationship


# CRUD for factor


def load_factor_by_id():
    pass


# CRUD for mapping rules




def post_data(data,event):
    pass


# CRUD for report
def create_report():
    pass


def load_reports():
    pass


# query for factors
def query_factor(factor_name:str):
    pass


# analyze
def analyze_master_space():
    pass


def analyze():
    # load pipeline by user and name
    # run first stage
    pass


def dashboard():
    pass


def view_report():
    pass


def customize_pipeline():
    pass


def use_default_pipeline(user):
    return True


# TODO master_space_analysis
def master_space_analysis():
    pass


def select_report():
    pass  #


def create_report():
    pass  #


# runtime import data
def import_raw_data():
    # save to mongodb
    # call mapping rule
    # rum factor engine
    pass
