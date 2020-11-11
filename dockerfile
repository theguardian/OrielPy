# The line below states we will base our new image on the Latest Official Ubuntu
FROM ubuntu:20.04

# Install important packages (git, python, etc)
RUN apt-get update && apt-get install python3.8 python3.8-dev python3.8-distutils python3-pip git gcc -y

# Identify the maintainer of an image
LABEL maintainer="justin.evans@gmail.com"

# Establish base directory on image
WORKDIR /srv

# Clone OrielPy
RUN git clone https://github.com/theguardian/orielpy

# Establish Workdir
WORKDIR /srv/orielpy

# Install necessary python packages
RUN pip3 install -r requirements.txt

# Expose port 5151
EXPOSE 5151

# Command to start service
CMD python3 CherryStrap.py
