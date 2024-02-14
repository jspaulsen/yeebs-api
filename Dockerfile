FROM python:3.11-bookworm AS base

ENV DBMATE_URL="https://github.com/amacneil/dbmate/releases/latest/download/dbmate-linux-amd64"


# Install dependencies
RUN \
    apt-get update && \
    apt-get install -y \
        curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


# Install dbmate
RUN \
    curl -fsSL -o /usr/local/bin/dbmate $DBMATE_URL && \
    chmod +x /usr/local/bin/dbmate

RUN \
    mkdir -p /build

WORKDIR /build

# Install pipenv
RUN \
    pip install pipenv


# Copy in the Pipfile and Pipfile.lock and install the dependencies
COPY Pipfile Pipfile.lock /build/

RUN \
    pipenv requirements > /build/requirements.txt



# Production Layer; this is the target image
FROM python:3.11-bookworm AS production


# Make the application directory and user
RUN \
    useradd -m app && \
    mkdir -p /app

USER app
WORKDIR /app


# Copy dbmate from the base image
COPY --from=base /usr/local/bin/dbmate /usr/local/bin/dbmate

# Copy in the requirements file and install the dependencies
COPY --from=base --chown=app:app /build/requirements.txt /app/

# Copy dependencies
RUN \
    pip install \
    --no-cache-dir \
    -r requirements.txt

# Copy application files
COPY --chown=app:app . /app

# uvicorn is included in dependencies
ENTRYPOINT [ "python", "-m", "uvicorn", "app.main:api" ]