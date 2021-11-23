from watchmen.console_space.model.favorite import Favorite
from watchmen.database.find_storage_template import find_storage_template

CONSOLE_SPACE_FAVORITES = "console_space_favorites"


# template = find_template()

storage_template = find_storage_template()


def create_favorite(favorite):
    # return template.create(CONSOLE_SPACE_FAVORITES, favorite, Favorite)
    return storage_template.insert_one(favorite, Favorite, CONSOLE_SPACE_FAVORITES)


def save_favorite(favorite, current_user):
    result = load_favorite(favorite.userId, current_user)
    if result is not None:
        update_favorite(favorite.userId, favorite)
    else:
        create_favorite(favorite)
    return favorite


def load_favorite(user_id, current_user):
    # return template.find_one(CONSOLE_SPACE_FAVORITES, {"userId": user_id}, Favorite)
    return storage_template.find_one({"and": [{"userId": user_id}, {"tenantId": current_user.tenantId}]}, Favorite,
                    CONSOLE_SPACE_FAVORITES)


def update_favorite(user_id, favorite: Favorite):
    # return template.update_one(CONSOLE_SPACE_FAVORITES, {"userId": user_id}, favorite)
    return storage_template.update_one(favorite, favorite, CONSOLE_SPACE_FAVORITES)
