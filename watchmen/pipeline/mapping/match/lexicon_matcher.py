from watchmen.knowledge.knowledge_loader import load_lexicon
from watchmen.lake.model_schema import ModelSchema
import spacy;
nlp = spacy.load('en_core_web_sm')
import decamelize


# TODO[next] add ref id to filed_schema
def lexicon_match(model_schema: ModelSchema):
    keys = model_schema.businessFields.keys()
    # values = model_schema.businessFields.values()
    field_names = " ".join(keys)
    lexicon_lib = load_lexicon(model_schema.domain, "en")

    lexicon_str = " ".join(lexicon_lib.keys())

    tokens = nlp(field_names)

    lexicon_tokens  = nlp(lexicon_str)

    # TODO[future] need to optimize performance
    # TODO【BUG】 find duplicate tokens
    # TODO[?] split field_names base on camelize
    lexicon_match_results = []

    for import_token in tokens:
        for lexicon_token in lexicon_tokens:
            if import_token.has_vector:
                similarity = import_token.similarity(lexicon_token)
                if similarity > 0.7:
                    lexicon_match_results.append(
                        {"source": import_token.text, "target": lexicon_token.text, "similarity": str(similarity)})

    return lexicon_match_results
















