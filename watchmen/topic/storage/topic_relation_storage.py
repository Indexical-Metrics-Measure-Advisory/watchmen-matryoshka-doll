from watchmen.common.storage.engine.storage_engine import get_client
from watchmen.topic.topic_relationship import TopicRelationship

db = get_client()

topic_relation_collections = db.get_collection('topic_relation_collections')


def save_topic_relationship(topic_relation: TopicRelationship):
    result = load_relationship_by_source_id_and_target_id(topic_relation.sourceTopicId, topic_relation.targetTopicId)
    print(result)
    if result:
        topic_relation_collections.update_one({"relationId": result["relationId"]}, {"$set": topic_relation.dict()})
    else:
        topic_relation_collections.insert(topic_relation.dict())
    return TopicRelationship.parse_obj(topic_relation)


def load_relationship_by_source_id_and_target_id(soure_topic_id, target_topic_id):
    result = topic_relation_collections.find_one({"sourceTopicId": soure_topic_id, "targetTopicId": target_topic_id})
    return result


def load_relationships_by_topic_ids(topic_ids):
    result = topic_relation_collections.find({"sourceTopicId": {"$in": topic_ids}})
    # print("result",result)
    return list(result)


def load_relationships_by_topic_ids_target(topic_ids):
    result = topic_relation_collections.find({"targetTopicId": {"$in": topic_ids}})
    # print("result",result)
    return list(result)
