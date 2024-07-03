# Use the official image as a parent image
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 8080

# Define environment variable
ENV PYTHONUNBUFFERED=1

# Run app.py when the container launches
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
