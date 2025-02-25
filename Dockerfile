# Stage 1: Build stage
FROM python:3.13-bullseye AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

RUN apt-get update && apt-get install -y gcc libc-dev

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Collect static files
RUN python /app/opportunity_tracker/manage.py collectstatic --noinput

# Stage 2: Production stage
FROM python:3.13-bullseye

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Copy only the necessary files from the build stage
COPY --from=builder /app /app

# Set working directory to your Django project folder
WORKDIR /app/opportunity_tracker

# Add a user to run the application
RUN adduser --disabled-password --gecos '' django_user
RUN chown -R django_user:django_user /app
USER django_user

# Copy the Python dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Expose the port the app runs on
EXPOSE 8000

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "opportunity_tracker.wsgi:application"]

