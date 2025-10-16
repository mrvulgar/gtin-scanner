FROM python:3.11-slim-bookworm

# System deps (keep minimal)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       libglib2.0-0 libgl1 ca-certificates libdmtx0b fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    GRADIO_SERVER_NAME=0.0.0.0

WORKDIR /app

# Copy dependency definitions first for better caching
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application code
COPY . /app

# Create non-root user
RUN useradd -ms /bin/bash appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 7860

# Default command runs Gradio directly, disabling API schema rendering to avoid known bug
CMD ["python", "-u", "run_app.py"]


