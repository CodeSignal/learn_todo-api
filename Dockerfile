# Use Python 3.10.6 as the base image for the container
FROM python:3.10.6

# Copy the requirements.txt file to the container's root directory
COPY requirements.txt .

# Install Python dependencies listed in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8000 to make the Flask app accessible
# This is a documentation instruction and does not map the port to the host
EXPOSE 8000

# Copy the app folder containing the Flask application to /app in the container
COPY app /app

# Set the working directory to /app
WORKDIR /app

# Run the Flask app when the container starts
CMD ["python", "main.py"]
