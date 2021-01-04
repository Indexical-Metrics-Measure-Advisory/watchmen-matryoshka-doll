from enum import Enum


class RuleType(str, Enum):
    natural_language = "nlp"
    dsl = "dsl"


class DSLType(str, Enum):
    groovy = "groovy"
    typescript = "typescript"



