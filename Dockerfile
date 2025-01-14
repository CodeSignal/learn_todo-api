# Use Python 3.10.6 base image
FROM python:3.10.6

# Set the working directory in the container
WORKDIR /app

# Copy the entire application directory to the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8000 for the Flask app
EXPOSE 8000

# Command to run the Flask app
CMD ["python", "main.py"]
