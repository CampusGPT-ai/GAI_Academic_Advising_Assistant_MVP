# Use an official Python runtime as a parent image
FROM python:3.11-slim-bookworm

# Set the working directory in the container
WORKDIR /

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends gcc

RUN pip install poetry
# Copy the project files into the container
COPY pyproject.toml poetry.lock ./

# Install project dependencies (excluding development dependencies)
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-root

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Inform Docker that the container is listening on the specified port at runtime.
EXPOSE 80

CMD ["gunicorn", "-c", "gunicorn.conf.py", "main:app"]