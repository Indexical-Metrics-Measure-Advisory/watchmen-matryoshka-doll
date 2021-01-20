from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.common.storage.engine.storage_engine import get_client
from watchmen.common.utils.data_utils import WATCHMEN
from watchmen.dashborad.model.dashborad import ConsoleDashboard

db = get_client(WATCHMEN)
console_dashboard_collection = db.get_collection('console_dashboard')


def create_dashboard_to_storage(dashboard: ConsoleDashboard):
    dashboard.dashboardId = get_surrogate_key()
    console_dashboard_collection.insert_one(dashboard.dict())
    return ConsoleDashboard.parse_obj(dashboard)


def update_dashboard_to_storage(dashboard: ConsoleDashboard):
    console_dashboard_collection.update_one({"dashboardId": dashboard.dashboardId}, {"$set": dashboard.dict()})
    return ConsoleDashboard.parse_obj(dashboard)


def load_dashboard_by_id(dashboard_id):
    result = console_dashboard_collection.find_one({"dashboardId": dashboard_id})
    return ConsoleDashboard.parse_obj(result)


def load_dashboard_by_user_id(user_id):
    result = console_dashboard_collection.find({"userId": user_id})
    return list(result)


def delete_dashboard_by_id(dashboard_id):
    console_dashboard_collection.delete_one({"dashboardId": dashboard_id})


def rename_dashboard_by_id(dashboard_id,name):
    console_dashboard_collection.update_one({"dashboardId":dashboard_id }, {"$set": {"name":name}})
    # return ConsoleDashboard.parse_obj(dashboard)