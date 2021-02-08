FROM python:3.7

WORKDIR /app
ADD . .
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install
RUN pip install uvicorn
#RUN python -m spacy download en_core_web_sm


EXPOSE 8000
CMD ["uvicorn","watchmen.main:app","--host", "0.0.0.0", "--port", "80","--workers","$WORKERS_NUM"]






