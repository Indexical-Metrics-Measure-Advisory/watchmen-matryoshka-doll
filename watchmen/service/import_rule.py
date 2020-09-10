import spacy
from spacy.matcher import Matcher
from spacy.symbols import nsubj, CCONJ, nmod, acomp, dobj, prep, pobj, ADJ,xcomp,nsubjpass,attr
from spacy.tokens import Token

from watchmen.schema.rule_context import RuleContext

IF = "if_sentence"
THEN = "then_sentence"


def find_cconj(if_docs):
    return filter(lambda token: token.pos is CCONJ, if_docs)


def spilt_by_cconj(if_docs, index_list):
    conditions = []
    for i, v in enumerate(index_list):
        if i + 1 < len(index_list):
            start = v
            if v is not 0:
                start = v + 1
            end = index_list[i + 1]
            conditions.append(if_docs[start:end])
    return conditions


def is_and(cconjs):
    #TODO[next] check empty
    return all(x.lemma_ == "and" for x in cconjs)


def find_nsubj(children: list):
    return list(filter(lambda x: x.dep == nsubj or x.dep==nsubjpass, children))


# def find_value(children:list):
#     return


def find_nmod_or_compound(children):
    return list(filter(lambda x: x.dep == nmod or x.dep_ == "compound", children))


def _find_factor(root: Token):
    nsubj_tokens = find_nsubj(list(root.children))
    factor = {}
    if len(nsubj_tokens) is 1:
        token = nsubj_tokens[0]
        # print(token)
        factor["factor"] = token.text
        result = find_nmod_or_compound(token.children)
        if len(result) == 1:
            factor["domain"] = result[0].text
            # pass

    return factor


def _find_value(root: Token):
    result = list(filter(lambda x: x.dep == acomp or x.dep == dobj or x.dep == pobj or x.dep==xcomp or x.dep ==attr, root.children))
    if len(result) is 1:
        return result[0].text
    # value={}

    return None


def is_not_op(op:Token):
    return op.dep == acomp and op.pos == ADJ and list(op.children) == []


def have_sub_op(root, operate):
    result = list(
        filter(lambda x: x.dep == prep or (x.dep == acomp and x.pos == ADJ), root.children))

    if len(result) is 1:
        token = result[0]
        if is_not_op(token):
            return operate
        else:
            operate.append(token)
            have_sub_op(token, operate)

    return operate


def _find_operate(root: Token):
    operates = []
    operates.append(root)

    have_sub_op(root, operates)
    return operates


def convent_to_str(operates):
    result = map(lambda x:x.text,operates)

    # print()
    return list(result)


def import_single_rule(rule_context: RuleContext, rule: str):
    # split rule base on sentence
    nlp = spacy.load("en_core_web_sm")
    match_result = root_match(nlp, rule)
    # print(match_result)
    rule_schema = {}

    if IF in match_result:
        match_text = match_result[IF].text
        rule_schema["if"] = {}
        if_docs = nlp(match_text.replace("if", ""))
        cconjs = list(find_cconj(if_docs))
        if is_and(cconjs):
            rule_schema["if"]["and"] = []
            index_list = build_index_list(cconjs, if_docs)
            # print(index_list)
            conditions = spilt_by_cconj(if_docs, index_list)
            for condition in conditions:
                doc = nlp(condition.text)
                result = {}
                # print("nlp: ", condition)
                for sent in doc.sents:
                    # print("root:", sent.root)
                    operate = _find_operate(sent.root)
                    factor = _find_factor(sent.root)
                    value = _find_value(operate[-1])
                    result["factor"] = factor
                    result["operate"] = convent_to_str(operate)
                    result["value"] = value
                    rule_schema["if"]["and"].append(result)

    if THEN in match_result:
        match_text = match_result[THEN].text
        # print(match_text)
        rule_schema["then"] = {}
        then_docs = nlp(match_text.replace("then", ""))
        for sent in then_docs.sents:
            # print(sent.root)
            result = {}
            operate = _find_operate(sent.root)
            factor = _find_factor(sent.root)
            # print(factor)
            value = _find_value(operate[-1])
            result["factor"]=factor
            result["operate"] = convent_to_str(operate)
            result["value"] = value
            rule_schema["then"]=result

    # TODO[next] match factor to domain and basic schema
    # TODO[future] generate report for rules
    return rule_schema


def build_index_list(cconjs, if_docs):
    index_list = [0]
    for c in cconjs:
        index_list.append(c.i)
    index_list.append(len(if_docs))
    return index_list


def root_match(nlp, rule):
    if_pattern = [{'LOWER': 'if'},
                  {'OP': '*'},
                  {'TEXT': ','}]

    then_pattern = [{'LOWER': 'then'}, {'OP': '*'}, {"IS_PUNCT": True}]
    doc = nlp(rule)
    matcher = Matcher(nlp.vocab)
    matcher.add(IF, None, if_pattern)
    matcher.add(THEN, None, then_pattern)
    matches = matcher(doc)
    match_result = {}
    for match_id, start, end in matches:
        string_id = nlp.vocab.strings[match_id]  # Get string representation
        span = doc[start:end]  # The matched span
        # print(string_id, span.text)
        match_result[string_id] = span
    return match_result


def build_rule_schema():
    # nlp match
    # match noun with schema schema and domain schema
    # generate basic schema

    pass