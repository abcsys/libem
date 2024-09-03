# use an official Python runtime as a parent image
FROM python:3.12

# set the working directory to /serve
WORKDIR /serve

# copy the current directory contents into the container
ADD . /serve

# install the needed packages
RUN pip install libem && \
    mkdir /root/.libem && \
    touch /root/.libem/config.yaml && \
    git clone --depth 1 https://github.com/abcsys/libem-sample-data.git /usr/local/lib/python3.12/libem-sample-data

# expose port 8000
EXPOSE 8000

# run serve.py when the container launches
CMD ["python", "serve.py"]