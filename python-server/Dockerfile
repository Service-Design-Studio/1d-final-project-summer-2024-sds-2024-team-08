# Use the official image as a parent image
FROM python:3.10.14-alpine3.20

RUN apk update && apk upgrade && apk add libpq-dev build-base geos geos-dev

RUN pip install shapely

RUN pip install fastapi langchain langgraph

COPY requirements.txt requirements.txt
# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

COPY . .

# Make port 80 available to the world outside this container
EXPOSE 8080

# Define environment variable
ENV PYTHONUNBUFFERED=1

# Run app.py when the container launches
CMD ["uvicorn", "--app-dir", "app", "--host", "0.0.0.0", "--port", "8080", "main:app"]