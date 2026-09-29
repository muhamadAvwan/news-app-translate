FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=7860

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Unduh & pasang model Argos en->id saat build supaya start cepat
RUN python -c "import argostranslate.package as p; \
avail = p.get_available_packages(); \
pkg = next(x for x in avail if x.from_code=='en' and x.to_code=='id'); \
p.install_from_path(pkg.download())"

EXPOSE 7860

HEALTHCHECK --interval=60s --timeout=15s --start-period=120s --retries=3 \
  CMD curl -sf http://localhost:${PORT}/health || exit 1

CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT} --workers 1"]
