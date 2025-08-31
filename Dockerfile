# Use a minimal Python image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install required packages
# pandas for reading CSV
# requests for making API calls to the model
RUN pip install pandas requests influxdb-client

# Copy the Python script and the CSV file into the container
# The CSV is mounted at runtime via docker-compose
COPY process_data.py .
COPY helper_data_sources.py .