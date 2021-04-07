from watchmen.common.storage.engine_adaptor import find_template
from watchmen.common.storage.storage_template import insert_one, find_by_id, update_one
from watchmen.console_space.model.favorite import Favorite

CONSOLE_SPACE_FAVORITES = "console_space_favorites"

# template = find_template()


def create_favorite(favorite):
    # return template.create(CONSOLE_SPACE_FAVORITES, favorite, Favorite)
    return insert_one(favorite, Favorite, CONSOLE_SPACE_FAVORITES)


def save_favorite(favorite):
    result = load_favorite(favorite.userId)
    if result is not None:
        update_favorite(favorite.userId, favorite)
    else:
        create_favorite(favorite)
    return favorite


def load_favorite(user_id):
    # return template.find_one(CONSOLE_SPACE_FAVORITES, {"userId": user_id}, Favorite)
    return find_by_id(user_id, Favorite, CONSOLE_SPACE_FAVORITES)


def update_favorite(user_id, favorite: Favorite):
    # return template.update_one(CONSOLE_SPACE_FAVORITES, {"userId": user_id}, favorite)
    return update_one(favorite, favorite, CONSOLE_SPACE_FAVORITES)