FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

# Tectonic is a self-contained LaTeX engine; install the prebuilt binary
# rather than pulling in a full TeX Live distribution.
RUN curl --proto '=https' --tlsv1.2 -fsSL https://drop-sh.fullyjustified.net | sh \
    && mv tectonic /usr/local/bin/tectonic \
    && tectonic --version

WORKDIR /app
COPY pyproject.toml README.md ./
COPY resume_tailor ./resume_tailor
COPY examples ./examples

RUN pip install --no-cache-dir ".[api]"

EXPOSE 8080
CMD ["uvicorn", "resume_tailor.api:app", "--host", "0.0.0.0", "--port", "8080"]
