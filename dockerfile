# Use an official Python runtime as a parent image
FROM python:3.10-slim-bullseye

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5000 for the Flask app
EXPOSE 5005

# Set the entrypoint to run the Flask app
ENTRYPOINT ["python", "faq.py"]
