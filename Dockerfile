FROM python:3.11-slim-bullseye

# Define some environment variables
ENV PIP_NO_CACHE_DIR=true \
    DEBIAN_FRONTEND=noninteractive

# Install dependencies needed to download/install packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    apt-utils \
    curl \
    cron

# We want to run things as a non-privileged user
ENV USERNAME=user
ENV PATH="$PATH:/home/$USERNAME/.local/bin"

# Add user and set up a workdir
RUN useradd -m $USERNAME
WORKDIR /home/$USERNAME/app
RUN chown $USERNAME.$USERNAME .

# Make cron suid root, so it can be started by a user.
RUN chmod u+s /usr/sbin/cron

# Everything below here runs as a non-privileged user
USER $USERNAME

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python - --version 1.5.1
RUN poetry config virtualenvs.in-project true

# Install runtime dependencies (will be cached)
COPY --chown=$USERNAME:$USERNAME pyproject.toml poetry.lock ./
RUN poetry install --only main --no-root

# Copy project files to container
COPY --chown=$USERNAME:$USERNAME src ./src

# Install our own package
RUN poetry install --only main

# Install crontab for $USERNAME
COPY --chown=$USERNAME:$USERNAME crontab ./
RUN crontab ./crontab

# Start shell script
COPY --chown=$USERNAME:$USERNAME entrypoint.sh ./
CMD ["./entrypoint.sh"]
