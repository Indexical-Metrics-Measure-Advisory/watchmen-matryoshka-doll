from fastapi import APIRouter, Depends

from watchmen.auth.user import User
from watchmen.common import deps
from watchmen.common.pagination import Pagination
from watchmen.space.storage.space_storage import load_space_list_by_user_id_with_pagination

router = APIRouter()


# Console API


# TODO console api


@router.post("/space/me", tags=["console"])
async def load_space_list_by_user(pagination: Pagination,current_user: User = Depends(deps.get_current_user)):
    return load_space_list_by_user_id_with_pagination(current_user["groupIds"], pagination)




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


async def share_dashboard_url(to: str):
    pass
