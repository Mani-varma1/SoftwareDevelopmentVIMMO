#FROM python:3.13
#
## Update the package list and upgrade installed packages
#RUN apt-get update && apt-get -y upgrade
#
## Install sqlite3 \
#RUN apt-get install -y sqlite3
#
##RUN git clone --branch docker-test --single-branch https://github.com/Itebbs22/SoftwareDevelopmentVIMMO /app
#
#WORKDIR /app
#
#COPY . /app
#
## Upgrade pip
#RUN pip install --upgrade pip
#
## Install Python packages defined in the current project
#RUN pip install -e .
#
## Keep the container running (optional, for debugging or persistence)
#CMD ["tail", "-f", "/dev/null"]





# Use Python 3.13 as the base image
FROM python:3.13

# Update the package list and upgrade installed packages
RUN apt-get update && apt-get -y upgrade

# Install sqlite3 for the database
RUN apt-get install -y sqlite3

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Upgrade pip
RUN pip install --upgrade pip

# Install Python packages defined in the current project
RUN pip install -e .

# Expose port 5001 to the outside world
EXPOSE 5001

# Run the application (main.py) when the container starts
CMD ["python", "vimmo/main.py"]