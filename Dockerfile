# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Install curl and clean up unnecessary files
RUN apt-get update && apt-get install -y curl && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /api

# Copy the dependencies file to the working directory
COPY ./requirements.txt /api/requirements.txt

# Sync all dependencies in the uv.lock file
RUN pip install -r requirements.txt

# Install any needed packages specified in requirements.txt
COPY . /api

EXPOSE 80

# Run main.py when the container launches
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]