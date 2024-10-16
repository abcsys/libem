# use an official Python runtime as a parent image
FROM python:3.12-slim

# set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD serve/serve /app
ADD serve/requirements.txt /app

# install requirements and libem
RUN pip install -r requirements.txt && \
    mkdir /root/.libem && \
    echo "" >> /root/.libem/config.yaml

# expose port 8080
EXPOSE 8080

# run run.py when the container launches
CMD ["python", "run.py"]
