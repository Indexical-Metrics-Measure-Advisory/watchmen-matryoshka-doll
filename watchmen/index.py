from bson import ObjectId
from fastapi import HTTPException

from watchmen.auth.index import get_current_user, check_promise
from watchmen.auth.user import User
from watchmen.factors.model.factor import Factor
from watchmen.factors.model.topic import Topic
from watchmen.knowledge.knowledge_loader import find_template_by_domain
from watchmen.lake.model_schema import ModelSchema
from watchmen.mapping.suggestion.generate_suggestion import generate_topic_suggestion, generate_factor_suggestion
from watchmen.master.index import create_master_space, add_topic_list_to_master, get_summary_for_master_space, \
    add_topic_to_master_space
from watchmen.pipeline.pipeline import build_default_pipeline
from watchmen.storage.mapping_rule_storage import save_topic_mapping_rule, load_topic_mapping_rule

from fastapi.encoders import jsonable_encoder

# auth
from watchmen.storage.topic_schema_storage import get_topic_list_by_ids


def auth_login(user:User):
    return True
    # pass


def  auth_logout(user:User):
    return True
    # pass


# design time data integration
def select_domain(domain: str):
    current_user = get_current_user()
    if check_promise(current_user):
        # find domain template
        topic_list = find_template_by_domain(domain)
        # create master space
        master_space = create_master_space(current_user,domain)
        # add template to master space
        master_space = add_topic_list_to_master(topic_list, master_space)
        # get summary for master_space
        return get_summary_for_master_space(master_space)
    else:
        raise HTTPException(status_code=401, detail="NO_PROMISE")


def generate_lake_schema(json_files, name):
    current_user = get_current_user()
    if check_promise(current_user):
        if use_default_pipeline(current_user):
            pipeline = build_default_pipeline()
            output_param = pipeline.run([json_files, name], {})
            # print(output_param)
            return output_param
        else:
            # load  customize_pipeline
            pass
            # TODO customize_pipeline run

        # pass
    else:
        raise HTTPException(status_code=401, detail="NO_PROMISE")

# CRUD for pipeline


def generate_suggestion_topic_service(lake_schema,master_schema):
    topic_id_list = master_schema.topic_id_list
    object_ids = map(lambda x: ObjectId(x), topic_id_list)
    topic_list = get_topic_list_by_ids(list(object_ids))
    return generate_topic_suggestion(lake_schema,topic_list)


def generate_suggestion_factor(lake_model: ModelSchema, topic: Topic):
    return generate_factor_suggestion(lake_model, topic)


def mapping_to_master(user, key: str):
    pass


def check_factor_is_exist():
    # check same factor and return similarity factor
    pass


def load_topic_mapping(model_schema_id,topic_id):
    return load_topic_mapping_rule(model_schema_id,topic_id)


def save_topic_mapping(topic_mapping_rule):
    return save_topic_mapping_rule(topic_mapping_rule)


#
# def update_factor_mapping():
#     pass #


def add_factor_to_master_topic(factor:Factor,master_space):

    # current_user = get_current_user()

    pass


def add_topic_to_master(topic, master_space):
    return  add_topic_to_master_space(topic, master_space)


# CRUD for master schema and relationship


# CRUD for factor


def load_factor_by_id():
    pass

# CRUD for mapping rules


# CRUD for report
def create_report():
    pass


def load_reports():
    pass


# query for factors
def query_factor():
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
def import_row_data():
    # save to mongodb
    # call mapping rule
    # rum factor engine
    pass
