FROM python:3.9.6-slim-buster

WORKDIR    /opt/oracle
RUN        apt-get update && apt-get install -y libaio1 wget unzip build-essential default-libmysqlclient-dev \
            && wget https://download.oracle.com/otn_software/linux/instantclient/213000/instantclient-basiclite-linux.x64-21.3.0.0.0.zip \
            && unzip instantclient-basiclite-linux.x64-21.3.0.0.0.zip \
            && rm -f instantclient-basiclite-linux.x64-21.3.0.0.0.zip \
            && cd /opt/oracle/instantclient* \
            && rm -f *jdbc* *occi* *mysql* *README *jar uidrvci genezi adrci \
            && echo /opt/oracle/instantclient* > /etc/ld.so.conf.d/oracle-instantclient.conf \
            && ldconfig

WORKDIR /app
ADD . .
RUN pip install cx_Oracle
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install -E mysql -E mongo -E rabbit -E kafka
RUN pip install watchmen-storage-engine
RUN pip install watchmen-model==15.2.14
RUN pip install watchmen-boot

EXPOSE 8000
CMD ["uvicorn","watchmen.main:app","--host", "0.0.0.0", "--port", "80"]






