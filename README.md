<p align="center">
    <a href="https://www.watchmen.com/"><img alt="Watchmen Logo" src="doc/image/logo.png" /></a>
</p>
<p align="center">
    <b>watchmen is a lighter platform for data analytics.</b>
</p>
<p align="center">
    See the <a href="https://www.watchmen.com/docs/current/">User Manual</a> for deployment instructions and end user documentation.
</p>


# Overview

<p align="center">
<img alt="Architecture Diagram" src="doc/image/architecture.png" />
</p>

watchman-data-processor is the back-end server for the watchmen data platform. 

# Use Case

<p align="center">
<img alt="Architecture Diagram" src="doc/image/usecase.png" />
</p>


# build requirements

* Mac OS X or Linux or Windows
* Python 3.7+, 64-bit
* Docker

# start
local start

```
python app.py
```

# docker run

```
docker run --name watchmen-data-processor -v /usr/watchmen/watchmen-data-processor/temp/rotating.log:/app/temp/rotating.log --env-file /usr/watchmen/watchmen-data-processor/env.list -p 8000:80 -d  ghcr.io/indexical-metrics-measure-advisory/watchmen-data-processor:latest
```

# configuration

```
PROJECT_NAME=matryoshka
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_MONITOR_HOST=localhost
MONGO_MONITOR_PORT=27017
PRESTO_HTTP_URL=http://localhost:8080
PRESTO_HOST=localhost
PRESTO_PORT=8080
WORKERS_NUM=2
```

# presto configuration

```
connector.name=mongodb
mongodb.seeds=localhost:27017
```