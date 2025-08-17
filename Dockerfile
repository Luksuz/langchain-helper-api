FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install wkhtmltopdf (available in Debian Bookworm) and clean up apt lists
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        wkhtmltopdf \
        fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

COPY src /app/src
COPY assets /app/assets
COPY v0_prompt.md /app/v0_prompt.md

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
