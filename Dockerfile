# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /jobfind

# Copy the current directory contents into the container at /app
COPY . /jobfind

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r app/requirements.txt

# Install watchdog for auto-reloading
RUN pip install watchdog

EXPOSE 5001

# Define environment variables
ENV FLASK_APP=main.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_DEBUG=1
ENV FLASK_RUN_PORT=5001

# Run flask when the container launches 
CMD ["flask","--app=main.py", "run", "--debug", "--host=0.0.0.0"]
