from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.common.storage.engine.storage_engine import get_client
from watchmen.common.storage.engine_adaptor import find_template
from watchmen.common.utils.data_utils import check_fake_id
from watchmen.dashborad.model.dashborad import ConsoleDashboard

DASHBOARDS = "console_dashboards"


template = find_template()


def create_dashboard_to_storage(dashboard: ConsoleDashboard):
    if dashboard.dashboardId is None or check_fake_id(dashboard.dashboardId):
        dashboard.dashboardId = get_surrogate_key()

    return template.create(DASHBOARDS,dashboard,ConsoleDashboard)


def update_dashboard_to_storage(dashboard: ConsoleDashboard):

    return template.update_one(DASHBOARDS,{"dashboardId": dashboard.dashboardId},dashboard,ConsoleDashboard)


def load_dashboard_by_id(dashboard_id)->ConsoleDashboard:

    return template.find_one(DASHBOARDS,{"dashboardId": dashboard_id},ConsoleDashboard)


def load_dashboard_by_user_id(user_id):

    return template.find(DASHBOARDS,{"userId": user_id},ConsoleDashboard)


def delete_dashboard_by_id(dashboard_id):

    return template.delete_one(DASHBOARDS,{"dashboardId": dashboard_id})


def rename_dashboard_by_id(dashboard_id, name):

    return template.update_one(DASHBOARDS,{"dashboardId": dashboard_id},{"name": name},ConsoleDashboard)


def import_dashboard_to_db(dashboard):

    template.create(DASHBOARDS,dashboard,ConsoleDashboard)
