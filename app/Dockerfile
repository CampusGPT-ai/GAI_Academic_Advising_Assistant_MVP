# Use an official Python runtime as a parent image
FROM python:3.11-slim-bookworm as builder


WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    g++ \
    libpq-dev \
    unixodbc-dev \
    curl \
    apt-transport-https \
    ca-certificates \
    gnupg \
    build-essential \
    libssl-dev \
    libasound2 \
    wget \
    nginx

# Install Poetry
RUN pip install --trusted-host pypi.python.org poetry

# Copy project files (including pyproject.toml, poetry.lock)
COPY pyproject.toml poetry.lock* ./

ENV POETRY_HTTP_TIMEOUT=3000  


# Install dependencies using Poetry
RUN POETRY_VIRTUALENVS_CREATE=false poetry install

# Install NLTK and download the 'words' dataset
RUN poetry run pip install nltk && poetry run python -m nltk.downloader -d /usr/share/nltk_data words


FROM python:3.11-slim-bookworm
# Set the working directory in the run stage
WORKDIR /app

# Copy over the installed Python dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin


# Copy the NLTK data downloaded in the builder stage
COPY --from=builder /usr/share/nltk_data /usr/share/nltk_data
 
# Copy only the necessary files to run the application
COPY . .

# Expose the port your application listens on
EXPOSE 8000

# Define the command to run your app
CMD ["gunicorn", "-c", "gunicorn.conf.py", "app_server:app"]
