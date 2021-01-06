

# claim
# application
# broker , agent
# policy quotation ,binding
# customer ,

## Marketing

## Underwriting

## claims

## Reinsurance


## actuarial

## accounting


# Policy data
# Policy transactions (changes)
# Policy sections (coverages)
# Risk codes (specific values per product)
# Claims data
# Claim payments
# Claim outstanding estimate changes
# Collection data
# Client data
# from bson import timestamp
from pydantic import BaseModel
from pydantic.schema import datetime


class InsuranceTopics(BaseModel):
    id: str = None
    features: dict = None
    event: str = None
    insert_time: datetime = None


















