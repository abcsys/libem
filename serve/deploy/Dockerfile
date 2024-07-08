# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY libem /app
COPY serve /app
COPY requirements.txt /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Define environment variable
ENV FLASK_APP=serve/run.py

# Run app.py when the container launches
CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]
