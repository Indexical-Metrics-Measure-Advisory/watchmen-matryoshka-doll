FROM rackspacedot/python37

WORKDIR /app
ADD . .
RUN pip install -r requirements.txt
RUN python -m spacy download en_core_web_sm

EXPOSE 8000
CMD ["uvicorn","watchmen.main:app","--host", "0.0.0.0", "--port", "80"]






