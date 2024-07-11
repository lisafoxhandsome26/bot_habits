FROM python:3.12.3-alpine3.20

WORKDIR /src

COPY /backend /src/backend
COPY /config /src/config
COPY /database /src/database
COPY /shemases /src/shemases
COPY /main.py .
COPY config/requirements .


RUN pip install --upgrade pip "poetry==1.8.3"
RUN poetry config virtualenvs.create false --local
RUN poetry install