# Use a Python base image
FROM python:3.12

# Install dependencies
RUN pip install poetry toml

# Copy the version bump script into the Docker image
COPY bump_dev_version.py /bump_dev_version.py

# Set up Git user for commits
RUN git config --global user.email "github-actions[bot]@users.noreply.github.com" && \
    git config --global user.name "github-actions[bot]"

# Configure Git to use the GITHUB_TOKEN for authentication
ARG GITHUB_TOKEN
RUN git config --global credential.helper store && \
    echo "https://${GITHUB_TOKEN}:x-oauth-basic@github.com" > ~/.git-credentials

# Set the default entrypoint to execute the script
ENTRYPOINT ["python3", "/bump_dev_version.py"]
