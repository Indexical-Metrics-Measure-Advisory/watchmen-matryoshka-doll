import json
import os

import pandas as pd

os.chdir('D:/')

# Reading the json as a dict, policy information
with open('test1.json') as json_data:
    policy_data = json.load(json_data, encoding='utf-8')

print(policy_data)

# Reading the json as a dict, customer information
with open('customer_test.json') as json_data:
    customer_data = json.load(json_data, encoding='utf-8')

print(customer_data)

# df=pd.DataFrame.from_dict(data, orient='index').T.set_index('@pk')

policy_df = pd.DataFrame(policy_data).set_index('@pk')

print(policy_df)

customer_df = df = pd.DataFrame.from_dict(customer_data, orient='index').T.set_index('@pk')

print(customer_df)

join_df = policy_df.merge(customer_df, on='@pk')

# 显示所有列
pd.set_option('display.max_columns', None)
# 显示所有行
pd.set_option('display.max_raws', None)
# 设置value的显示长度为100，默认为50
pd.set_option('max_colwidth', 100)

print(join_df.values)
