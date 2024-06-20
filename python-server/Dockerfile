FROM python:3.12.4-slim

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r  requirements.txt

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

EXPOSE 8080
CMD gunicorn -k uvicorn.workers.UvicornWorker main:app