FROM python:3.9

WORKDIR /app
ADD . .
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install



EXPOSE 8000
CMD ["uvicorn","watchmen.main:app","--host", "0.0.0.0", "--port", "80"]






