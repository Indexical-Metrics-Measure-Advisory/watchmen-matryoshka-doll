from watchmen.common.sql_convert import generate_sql


def test_generate_sql():
    sql = generate_sql('policy',["age","date"],None)



    print(sql)