# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app code
COPY app/ ./app

# Expose the Flask port
EXPOSE 5000

# Set environment variable
ENV FLASK_APP=app/main.py

# Run the app
CMD ["python", "app/main.py"]
