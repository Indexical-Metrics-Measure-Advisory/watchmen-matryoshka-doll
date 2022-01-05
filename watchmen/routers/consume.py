from fastapi import APIRouter, Depends
from model.model.common.user import User


from watchmen.common import deps
from watchmen.console_space.storage.console_subject_storage import load_console_subject_by_name
from watchmen.report.engine.consume_engine import build_query_for_consume
from watchmen.report.model.consume_model import Query

router = APIRouter()


@router.post("/consume/dataset/query", tags=["console"])
async def query_dataset(query: Query, current_user: User = Depends(deps.get_current_user)):
    console_subject = load_console_subject_by_name(query.subject_name, current_user)
    data = build_query_for_consume(console_subject, query.indicators, query.where, current_user)
    return {"data": data}
