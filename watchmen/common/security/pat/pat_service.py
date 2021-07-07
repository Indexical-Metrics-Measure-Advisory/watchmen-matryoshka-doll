from watchmen.common.security.pat.pat_model import PersonAccessToken
from watchmen.common.security.pat.token_utils import create_token
from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.database.storage.storage_template import insert_one


def createPAT(note: str, user_id: str, tenant_id: str):
    pat = PersonAccessToken()
    pat.pat_id = get_surrogate_key()
    pat.token_id = create_token()
    pat.user_id = user_id
    pat.tenant_id = tenant_id
    pat.note = note
    insert_one(pat, PersonAccessToken, "pats")
    result = {'patId': pat.pat_id, 'note': pat.note, 'token': pat.token_id}
    return result


def queryPAT():
    pass

def deletePAT():
    pass

def verifyPAT():
    pass