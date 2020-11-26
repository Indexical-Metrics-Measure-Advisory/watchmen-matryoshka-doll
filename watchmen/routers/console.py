from fastapi import APIRouter

router = APIRouter()


@router.get("/space/me", tags=["console"])
async def load_space_list_by_user():
    pass


async def load_space_by_id(id: str):
    pass




## Console API


## TODO console api

async def load_space_list_by_user():
    pass


async def load_space_by_id(id: str):
    pass


async def sort_space_by_sort_type():
    pass


async def load_dashboard_list_by_user():
    pass


async def load_dashboard_by_id(id: str):
    pass

# async def sort_space_by_sort_type():
#     pass


async def connect_to_space():
    pass


async def create_dashboard():
    pass


async def load_subject_by_group():
    pass


async def add_subject_to_group():
    pass


async def load_subject_groups_by_space_id():
    pass


async def load_available_resources_by_space_id():
    pass


async def save_subject_definition():
    pass


async def load_subject_definition():
    pass


async def load_instance_data_by_subject_id():
    pass


async def load_reports_by_subject_id():
    pass


async def share_dashboard_url(to:str):
    pass