from fastapi import HTTPException

from watchmen.auth.index import get_current_user, check_promise
from watchmen.knowledge.knowledge_loader import find_template_by_domain
from watchmen.master.index import create_master_space, add_topic_list_to_master, get_summary_for_master_space
from watchmen.pipeline.pipeline import build_default_pipeline


# auth


def login():
    pass


def logout():
    pass


# design time data integration

def select_domain(domain: str):
    current_user = get_current_user()
    if check_promise(current_user):
        # find domain template
        topic_list = find_template_by_domain(domain)
        # create master space
        master_space = create_master_space(current_user)
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

# create relationship for master schema

def mapping_to_master(user, key: str):
    pass


def add_topic_to_master():
    pass


def update_topic_mapping():
    pass #


def update_factor_mapping():
    pass #


def add_factor_to_master():
    pass #

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
