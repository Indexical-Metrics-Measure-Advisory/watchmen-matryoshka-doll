# 1. select basic domain for example insurance product ,marketing
# 2. read json from connector
# 3. generate basic schema base on json data
# 4. match schema with domain  knowledge dataset and provide suggestions
# 5. link knowledge domain to schema


from lib.connector.local_connector import row_data_load
from lib.model.model_schema import Domain
from lib.service.generate_schema import generate_schema


generate_schema("policy",row_data_load('../test/data/policy.json'),Domain.INSURANCE)

# TODO batch import data and get schema







# rule = "if the customer’s gender is male, the age is over 60, and the main clause limit exceeds 100W, then the underwriting level is set to advanced"







