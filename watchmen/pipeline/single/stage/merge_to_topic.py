

def init(**kwargs):
    topic_name = kwargs["topic_name"]

    def run(data):
        print(topic_name)
        print(data)
        return {"factor_a": "a", "factor_B": "b"}

    return run


def trigger(**kwargs) -> bool:
    return True
