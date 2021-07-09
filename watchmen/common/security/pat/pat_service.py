from typing import List

from watchmen.common.security.pat.pat_model import PersonAccessToken
from watchmen.common.security.pat.token_utils import create_token
from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.database.storage.storage_template import insert_one, find_one, list_all, delete_by_id, list_


def createPAT(note: str, user_id: str, username: str, tenant_id: str):
    pat = PersonAccessToken()
    pat.patId = get_surrogate_key()
    pat.tokenId = create_token()
    pat.userId = user_id
    pat.username = username
    pat.tenantId = tenant_id
    pat.note = note
    insert_one(pat, PersonAccessToken, "pats")
    result = {'patId': pat.patId, 'note': pat.note, 'token': pat.tokenId}
    return result


def queryPAT(tenantid):
    token_list: List[PersonAccessToken] = list_({"tenantid": tenantid}, PersonAccessToken, "pats")
    for token in token_list:
        token.tokenId = token.tokenId.replace(token.tokenId[4:-4], '*' * len(token.tokenId[4:-4]))
    return token_list


def deletePAT(patid):
    delete_by_id(patid, "pats")


def verifyPAT(token):
    return find_one({"tokenId": token}, PersonAccessToken, "pats")
