from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.common.utils.data_utils import check_fake_id
from watchmen.dashborad.model.dashborad import ConsoleDashboard
from watchmen.database.storage.storage_template import insert_one, update_one, update_, find_, \
    find_one, delete_by_id

DASHBOARD_ID = "dashboardId"

DASHBOARDS = "console_dashboards"


# template = find_template()


def create_dashboard_to_storage(dashboard: ConsoleDashboard):
    if dashboard.dashboardId is None or check_fake_id(dashboard.dashboardId):
        dashboard.dashboardId = get_surrogate_key()
    # return template.create(DASHBOARDS, dashboard, ConsoleDashboard)
    return insert_one(dashboard, ConsoleDashboard, DASHBOARDS)


def update_dashboard_to_storage(dashboard: ConsoleDashboard):
    # return template.update_one(DASHBOARDS, {DASHBOARD_ID: dashboard.dashboardId}, dashboard, ConsoleDashboard)
    return update_one(dashboard, ConsoleDashboard, DASHBOARDS)


def load_dashboard_by_id(dashboard_id, current_user) -> ConsoleDashboard:
    # return template.find_one(DASHBOARDS, {DASHBOARD_ID: dashboard_id}, ConsoleDashboard)
    return find_one({"and": [{"dashboardId": dashboard_id}, {"tenantId": current_user.tenantId}]}, ConsoleDashboard,
                    DASHBOARDS)


def load_dashboard_by_user_id(user_id, current_user):
    # return template.find(DASHBOARDS, {"userId": user_id}, ConsoleDashboard)
    return find_({"and": [{"userId": user_id}, {"tenantId": current_user.tenantId}]}, ConsoleDashboard, DASHBOARDS)


def delete_dashboard_by_id(dashboard_id):
    # return template.delete_one(DASHBOARDS, {DASHBOARD_ID: dashboard_id})
    delete_by_id(dashboard_id, DASHBOARDS)


def rename_dashboard_by_id(dashboard_id, name):
    # return template.update_one(DASHBOARDS, {DASHBOARD_ID: dashboard_id}, {"name": name}, ConsoleDashboard)
    return update_({DASHBOARD_ID: dashboard_id}, {"name": name}, ConsoleDashboard, DASHBOARDS)


def import_dashboard_to_db(dashboard):
    # template.create(DASHBOARDS, dashboard, ConsoleDashboard)
    insert_one(dashboard, ConsoleDashboard, DASHBOARDS)
