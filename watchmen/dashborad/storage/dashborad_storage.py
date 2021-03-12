from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.common.storage.engine.storage_engine import get_client
from watchmen.common.storage.engine_adaptor import find_template
from watchmen.common.utils.data_utils import check_fake_id
from watchmen.dashborad.model.dashborad import ConsoleDashboard

DASHBOARDS = "console_dashboards"
#
# db = get_client()
# console_dashboards = db.get_collection('console_dashboards')

template = find_template()


def create_dashboard_to_storage(dashboard: ConsoleDashboard):
    if dashboard.dashboardId is None or check_fake_id(dashboard.dashboardId):
        dashboard.dashboardId = get_surrogate_key()
    # console_dashboards.insert_one(dashboard.dict())
    # return ConsoleDashboard.parse_obj(dashboard)
    return template.create(DASHBOARDS,dashboard,ConsoleDashboard)


def update_dashboard_to_storage(dashboard: ConsoleDashboard):
    # console_dashboards.update_one({"dashboardId": dashboard.dashboardId}, {"$set": dashboard.dict()})
    # return ConsoleDashboard.parse_obj(dashboard)
    return template.update_one(DASHBOARDS,{"dashboardId": dashboard.dashboardId},dashboard,ConsoleDashboard)


def load_dashboard_by_id(dashboard_id):
    # result = console_dashboards.find_one({"dashboardId": dashboard_id})
    # if result is None:
    #     return None
    # else:
    #     return ConsoleDashboard.parse_obj(result)
    return template.find_one(DASHBOARDS,{"dashboardId": dashboard_id},ConsoleDashboard)


def load_dashboard_by_user_id(user_id):
    # result = console_dashboards.find({"userId": user_id})
    # return list(result)
    return template.find(DASHBOARDS,{"userId": user_id},ConsoleDashboard)


def delete_dashboard_by_id(dashboard_id):
    # console_dashboards.delete_one({"dashboardId": dashboard_id})
    return template.delete_one(DASHBOARDS,{"dashboardId": dashboard_id})


def rename_dashboard_by_id(dashboard_id, name):
    # console_dashboards.update_one({"dashboardId": dashboard_id}, {"$set": {"name": name}})
    return template.update_one(DASHBOARDS,{"dashboardId": dashboard_id},{"name": name},ConsoleDashboard)


def import_dashboard_to_db(dashboard):
    # console_dashboards.insert_one(dashboard.dict())
    template.create(DASHBOARDS,dashboard,ConsoleDashboard)
