# use an official Python runtime as a parent image
FROM python:3.12

# set the working directory to /serve
WORKDIR /serve

# copy the current directory contents into the container
ADD serve /serve

# copy .env file
COPY arena.env /

# install libem and clone libem-sample-data
RUN pip install -r requirements.txt && \
    pip install git+https://github.com/abcsys/libem.git && \
    mkdir /root/.libem && \
    echo LIBEM_SAMPLE_DATA_PATH: /libem-sample-data >> /root/.libem/config.yaml && \
    git clone --depth 1 https://github.com/abcsys/libem-sample-data.git /libem-sample-data

# expose port 8000
EXPOSE 8000

# run serve.py when the container launches
CMD ["python", "serve.py"]
