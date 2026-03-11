# ifelse backend - production image
# Code execution is containerized (runner-* images). No host Java/Python/gcc.
FROM python:3.11-slim

WORKDIR /app

# Docker CLI only: backend runs code via `docker run` against runner images (no host runtimes)
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates curl \
    && DOCKER_VER=24.0.7 \
    && curl -fsSL "https://download.docker.com/linux/static/stable/x86_64/docker-${DOCKER_VER}.tgz" | tar xzf - -C /tmp \
    && mv /tmp/docker/docker /usr/local/bin/docker \
    && rm -rf /tmp/docker \
    && docker --version \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
