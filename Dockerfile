# Use a slim Python base image for a smaller footprint
FROM python:3.12-slim

# Set PYTHONUNBUFFERED to ensure real-time print output
ENV PYTHONUNBUFFERED=1

# Accept GITHUB_TOKEN as an argument
ARG GITHUB_TOKEN

# Configure Git with the GitHub token and install dependencies in a single RUN command
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    pip install --no-cache-dir poetry toml && \
    git config --global user.email 'github-actions[bot]@users.noreply.github.com' && \
    git config --global user.name 'github-actions[bot]' && \
    echo "https://${GITHUB_TOKEN}:x-oauth-basic@github.com" > ~/.git-credentials && \
    git config --global credential.helper "store --file=~/.git-credentials" && \
    git config --global --add safe.directory /github/workspace && \
    rm -rf /var/lib/apt/lists/*  # Clean up

# Copy the version bump script into the Docker image
COPY bump_dev_version.py /bump_dev_version.py

# Set the default entrypoint to execute the script
ENTRYPOINT ["python3", "/bump_dev_version.py"]
