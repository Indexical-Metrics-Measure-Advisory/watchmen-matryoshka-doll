from pypika import Query

from watchmen.common.utils.data_utils import build_collection_name
from watchmen.console_space.storage.console_subject_storage import load_console_subject_by_id
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id


def build_columns(columns):
   column=  columns[0]

   topic = get_topic_by_id(column.topicId)

   Query.from_(build_collection_name(topic.name))


    # Query.from_()
    # pass


def load_dataset_by_subject_id(subject_id):
    console_subject = load_console_subject_by_id(subject_id)

    dataset = console_subject.dataset



    if dataset is not None:
        # build columns
        if len(dataset.columns)>0:
            build_columns(dataset.columns)







    pass


