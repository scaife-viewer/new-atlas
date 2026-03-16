ARG PYTHON_VERSION=3.12-slim

FROM python:${PYTHON_VERSION}

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN mkdir /code

WORKDIR /code

COPY requirements.txt /tmp/requirements.txt
RUN set -ex && \
    pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    rm -rf /root/.cache/
COPY . /code

# RUN tar -xzf data.tar.gz

# RUN /code/manage.py shell -c "from atlas.texts.ingestion import ingest_texts; ingest_texts(reset=True)"
# RUN /code/manage.py shell -c "from atlas.texts.ingestion import tokenize_all_text_parts; tokenize_all_text_parts(reset=True)"
# RUN /code/manage.py shell -c "from atlas.dictionaries.ingestion import ingest_dictionaries;  ingest_dictionaries(reset=True)"
# RUN /code/manage.py shell -c "from atlas.commentaries.ingestion import ingest_commentaries; ingest_commentaries(reset=True)"

EXPOSE 8000

CMD ["gunicorn","--bind",":8000","atlas.wsgi"]
