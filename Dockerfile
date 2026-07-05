# Use official lightweight Python image
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y wget gnupg && \
    pip install --no-cache-dir playwright && \
    playwright install --with-deps && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Environment variables
ENV PORT=10000
EXPOSE 10000

# Start the Flask app with Gunicorn
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:${PORT}", "-w", "2"]
