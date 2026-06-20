# Use official lightweight Python image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=7860

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies (from backend subdirectory)
COPY backend/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend project files
COPY backend/ /app/

# Download spaCy models and train ML classifier during docker build
RUN python bootstrap.py

# Run migrations (SQLite)
RUN python manage.py migrate

# Expose port
EXPOSE 7860

# Start application using Gunicorn
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:7860", "--workers", "1", "--threads", "2", "--preload"]
