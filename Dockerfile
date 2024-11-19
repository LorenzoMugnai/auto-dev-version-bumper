# Use a slim Python base image for a smaller footprint
FROM python:3.12-slim

# Set PYTHONUNBUFFERED to ensure real-time print output
ENV PYTHONUNBUFFERED=1

# Accept GITHUB_TOKEN as an argument and set it as an environment variable
ARG GITHUB_TOKEN
ENV GITHUB_TOKEN=${GITHUB_TOKEN}

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    pip install --no-cache-dir poetry toml && \
    rm -rf /var/lib/apt/lists/*  # Clean up

# Copy the version bump script into the Docker image
COPY bump_dev_version.py /bump_dev_version.py

# Set the default entrypoint to execute the script, configuring Git user, authentication, and safe directory
ENTRYPOINT ["/bin/bash", "-c", \
    "git config --global user.email 'github-actions[bot]@users.noreply.github.com' && \
        git config --global user.name 'github-actions[bot]' && \
        git config --global --add safe.directory /github/workspace && \
        echo \"https://${GITHUB_TOKEN}:x-oauth-basic@github.com\" > ~/.git-credentials && \
        git config --global credential.helper 'store --file=~/.git-credentials' && \
        DEV_SUFFIX=${1} python3 /bump_dev_version.py"]
