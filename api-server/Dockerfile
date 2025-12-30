# Use Python 3.9 slim image
FROM python:3.9-slim

# Install system dependencies for pdf2image and tectonic
RUN apt-get update && apt-get install -y \
    poppler-utils \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install Tectonic
RUN wget -qO- https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic%400.15.0/tectonic-0.15.0-x86_64-unknown-linux-musl.tar.gz | tar xzf - -C /usr/local/bin

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Copy source code directory (for latex_converter)
COPY ../src /app/src

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8080

# Run the application
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
