from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.common.utils.data_utils import check_fake_id
from watchmen.space.space import Space
from watchmen.space.storage.space_storage import insert_space_to_storage, load_space_by_name, update_space_to_storage


def create_space(space: Space) -> Space:
    if space.spaceId is None or check_fake_id(space.spaceId):
        space.spaceId = get_surrogate_key()
    if type(space) is not dict:
        space = space.dict()

    insert_space_to_storage(space)
    return space


def update_space_by_id(space_id: str, space: Space) -> Space:
    if type(space) is not dict:
        space = space.dict()
    update_space_to_storage(space_id, space)
    return space


def load_space(name: str) -> Space:
    return load_space_by_name(name)
