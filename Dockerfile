FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/workspace

WORKDIR /workspace

COPY requirements.txt .
RUN pip install --no-cache-dir --timeout 300 --retries 5 -r requirements.txt

COPY . .

# Build deterministic local Manrope webfont assets.
RUN python scripts/fetch_manrope.py

EXPOSE 5000

CMD ["sh", "-c", "python scripts/wait_for_db.py && gunicorn --bind 0.0.0.0:5000 --workers 2 --threads 4 'app:create_app()'"]
