from watchmen.common.storage.engine.storage_engine import get_client
from watchmen.common.storage.engine_adaptor import find_template
from watchmen.console_space.model.favorite import Favorite

CONSOLE_SPACE_FAVORITES = "console_space_favorites"
#
# db = get_client()
# console_space_favorites = db.get_collection('console_space_favorites')

template= find_template()


def create_favorite(favorite):
    # console_space_favorites.insert(favorite.dict())
    return template.create(CONSOLE_SPACE_FAVORITES, favorite, Favorite)


def save_favorite(favorite):
    result = load_favorite(favorite.userId)
    if result is not None:
        update_favorite(favorite.userId, favorite)
    else:
        create_favorite(favorite)
    return favorite


def load_favorite(user_id):
    # favorite = console_space_favorites.find_one({"userId": user_id})
    # if favorite is None:
    #     return None
    # else:
    #     return favorite
    return template.find_one(CONSOLE_SPACE_FAVORITES,{"userId": user_id},Favorite)


def update_favorite(user_id, favorite: Favorite):
    # data = favorite.dict()
    # console_space_favorites.update_one({"userId": user_id}, {"$set": data})
    return template.update_one(CONSOLE_SPACE_FAVORITES,{"userId": user_id},data)
