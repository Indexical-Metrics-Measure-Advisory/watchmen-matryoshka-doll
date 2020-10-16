from watchmen.auth.index import get_current_user, check_promise
from watchmen.master.index import create_master_space


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


def select_domain(name: str):
    current_user = get_current_user()
    if check_promise(current_user):
        # find domain template
        # create master space
        master_space = create_master_space(current_user)
        # add template to master space
        # return description for master space

        pass
    else:
        return "error message"


def import_data(json_files):
    current_user = get_current_user()
    if check_promise(current_user):
        # save data to storage
        # generate import lake
        # generate data statistics
        # return data basic explore
        pass
    else:
        return "error message"



def master_space_analysis():
    pass #

def select_report():
    pass #

def create_report():
    pass #

















