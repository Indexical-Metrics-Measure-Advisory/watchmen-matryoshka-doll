

import prestodb

conn=prestodb.dbapi.connect(
    host='coordinator url',
    port=8443,
    user='the-user',
    catalog='the-catalog',
    schema='the-schema',
    http_scheme='https',
    auth=prestodb.auth.BasicAuthentication("principal id", "password"),
)


