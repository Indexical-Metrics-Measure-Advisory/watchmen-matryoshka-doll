import json
from datetime import datetime
from operator import eq

from sqlalchemy import update, select
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.orm import declarative_base

from watchmen.common.mysql.mysql_engine import engine
from watchmen.common.storage.collection_list import CollectionList
from watchmen.common.utils.data_utils import convert_to_dict

Base = declarative_base()


class ConsoleSpaceSubjectDao(Base):
    __tablename__ = CollectionList.console_subject

    subjectId = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    version = Column(Integer, nullable=False)
    _source = Column(JSON)
    create_time = Column(DateTime)
    last_modified = Column(DateTime)

    __mapper_args__ = {
        "version_id_col": version
    }


def create_console_subject(instance):
    console_space_subject = build_console_space_subject(instance)
    session = Session(engine, future=True)
    try:
        session.add(console_space_subject)
    except:
        session.rollback()
        raise
    else:
        session.commit()


def find_one_console_subject(query_dict):
    stmt = select(ConsoleSpaceSubjectDao)
    for key, value in query_dict:
        stmt = stmt.where(eq(getattr(ConsoleSpaceSubjectDao, key), value))
    session = Session(engine, future=True)
    result = session.execute(stmt)
    return result.fetchone()


def build_console_space_subject(instance):
    instance_dict: dict = convert_to_dict(instance)
    console_space_subject = ConsoleSpaceSubjectDao()
    console_space_subject.subjectId = instance_dict['subjectId']
    console_space_subject.name = instance_dict['name']
    console_space_subject.description = instance_dict['description']
    console_space_subject._source = json.dumps(instance_dict)
    console_space_subject.create_time = datetime.utcnow()
    console_space_subject.last_modified = datetime.utcnow()
    return console_space_subject


'''
def load_console_subject_list_by_ids(subject_id_list):

    return template.find(CONSOLE_SPACE_SUBJECTS, {"subjectId": {"$in": subject_id_list}}, ConsoleSpaceSubject)


def update_console_subject(console_subject: ConsoleSpaceSubject):

    return template.update_one(CONSOLE_SPACE_SUBJECTS, {"subjectId": console_subject.subjectId}, console_subject,
                               ConsoleSpaceSubject)


def load_console_subject_by_id(subject_id):

    return template.find_one(CONSOLE_SPACE_SUBJECTS, {"subjectId": subject_id}, ConsoleSpaceSubject)


def delete_console_subject_by_id(subject_id):

    return template.delete_one(CONSOLE_SPACE_SUBJECTS, {"subjectId": subject_id})


def delete_console_subject_by_ids(subject_ids):

    return template.remove(CONSOLE_SPACE_SUBJECTS, {"subjectId": {"$in": subject_ids}})


def rename_console_subject_by_id(subject_id, name):

    return template.update_one(CONSOLE_SPACE_SUBJECTS, {"subjectId": subject_id}, {"name": name},ConsoleSpaceSubject)


def load_console_subject_by_report_id(report_id):

    return template.find_one(CONSOLE_SPACE_SUBJECTS, {"reportIds": {"$in": [report_id]}}, ConsoleSpaceSubject)


def import_console_subject_to_db(subject):
    return template.create(CONSOLE_SPACE_SUBJECTS, subject, ConsoleSpaceSubject)
'''
