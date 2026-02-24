# ifelse backend - production image
FROM python:3.11-slim

WORKDIR /app

# Install system deps for optional code runtimes (node for JS; gcc/g++ for C/C++; openjdk for Java)
RUN apt-get update && apt-get install -y --no-install-recommends \
    nodejs \
    gcc g++ \
    openjdk-17-jdk-headless \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
