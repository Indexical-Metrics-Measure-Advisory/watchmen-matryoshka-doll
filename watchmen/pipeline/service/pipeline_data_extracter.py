#
#
# def extract_topic_relationship_from_pipeline(pipeline: Pipeline):
#     topic_relationships = []
#
#     for stage in pipeline.stages:
#         for unit in stage.units:
#             for action in unit.do:
#                 if action.type == "insert-or-merge-row" or action.type == "write-factor" or action.type == "merge-row" or action.type == "insert-row":
#                     if action.by:
#                         for children in action.by.children:
#                             topic_relationship = TopicRelationship()
#                             topic_relationship.sourceTopicId = children.left.topicId
#                             left_topic = get_topic_by_id(children.left.topicId)
#                             left_factor = get_factor(children.left.factorId, left_topic)
#                             topic_relationship.sourceFactorNames.append(left_factor.name)
#                             topic_relationship.relationId = get_surrogate_key()
#                             topic_relationship.targetTopicId = children.right.topicId
#                             right_topic = get_topic_by_id(children.right.topicId)
#                             right_factor = get_factor(children.right.factorId, right_topic)
#                             topic_relationship.targetFactorNames.append(right_factor.name)
#                             topic_relationship.type = "one-2-many"
#                             topic_relationships.append(topic_relationship)
#                         # print()
#
#     for topic_relationship in topic_relationships:
#         save_topic_relationship(topic_relationship)
#     return topic_relationships
