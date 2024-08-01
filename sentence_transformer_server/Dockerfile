FROM python:3.10.14-slim

COPY ./requirements.txt requirements.txt

# RUN pip install --upgrade pip

RUN pip install -r requirements.txt

COPY . .

# Make port 80 available to the world outside this container
EXPOSE 8080

# Define environment variable
ENV PYTHONUNBUFFERED=1

# Run app.py when the container launches
CMD ["uvicorn", "--app-dir", "app", "--host", "0.0.0.0", "--port", "8080", "main:app"]
