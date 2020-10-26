from fastapi import HTTPException

from watchmen.auth.index import get_current_user, check_promise
from watchmen.knowledge.knowledge_loader import find_template_by_domain
from watchmen.master.index import create_master_space, add_topic_list_to_master, get_summary_for_master_space
from watchmen.pipeline.pipeline import build_default_pipeline


def analyze():
    # load pipeline by user and name
    # run first stage
    pass


def dashboard():
    pass


def create_report():
    pass


def login():
    pass


def view_report():
    pass


def customize_pipeline():
    pass


def mapping_to_master():
    pass


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


def use_default_pipeline(user):
    return True


def import_data(json_files, name):
    current_user = get_current_user()
    if check_promise(current_user):
        if use_default_pipeline(current_user):
            pipeline = build_default_pipeline()
            output_param =pipeline.run([json_files,name], {})
            # print(output_param)
        else:
            ## load  customize_pipeline
            pass
            ##  run

        # pass
    # else:
    #     return "error message"


def master_space_analysis():
    pass  #


def select_report():
    pass  #


def create_report():
    pass  #
