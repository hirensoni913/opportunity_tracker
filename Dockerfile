# Stage 1: Build stage
FROM python:3.13-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


# RUN apt-get update && apt-get install -y \
#     libpango-1.0-0 \
#     libcairo2 \
#     libgdk-pixbuf2.0-0 \
#     libffi-dev \
#     shared-mime-info \
#     && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install dependencies
RUN pip install --upgrade pip
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production stage
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libcairo2 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    libglib2.0-0 \
    fonts-liberation \
    fonts-dejavu-core \
    shared-mime-info \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Add a user to run the application
RUN useradd -m -r django_user && \
    mkdir /app && \
    chown -R django_user /app
    
# Copy the Python dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Set work directory
WORKDIR /app

# Copy application code
COPY --chown=django_user . .

# Make entry file executable (before switching to non-root user)
RUN chmod +x /app/entrypoint.prod.sh

# Set working directory to your Django project folder
WORKDIR /app/opportunity_tracker

# Switch to non-root user
USER django_user

# Expose the port the app runs on
EXPOSE 8000

# Start the application 
CMD ["/app/entrypoint.prod.sh"]

