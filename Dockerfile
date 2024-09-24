# Use a lightweight Python 3.10 image
FROM python:3.10-slim

# Install system dependencies required for mysqlclient
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    libmariadb-dev-compat \
    libmariadb-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port Flask will run on
EXPOSE 5000

# Set environment variables for Flask
ENV FLASK_APP=app
ENV FLASK_ENV=production
ENV PYTHONPATH=/app:$PYTHONPATH

# Start the Flask application
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
