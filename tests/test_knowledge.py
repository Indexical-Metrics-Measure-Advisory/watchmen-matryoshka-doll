from watchmen.knowledge.knowledge_loader import find_template_by_domain


def test_load_template():
    template = find_template_by_domain("insurance")
    print(template)
    return template


