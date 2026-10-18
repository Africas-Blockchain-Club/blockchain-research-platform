# Base images are pinned by digest, so a rebuild uses exactly the image that was
# reviewed; Dependabot proposes digest updates as pull requests.
ARG PYTHON_IMAGE=python:3.12-slim@sha256:a6e34c598f2467ed0e9a8d349809fcd8b5c603269512df273a0bb1784edc11b1
ARG CADDY_IMAGE=caddy:2.11.7-alpine@sha256:d8542f48d34a9cf4e4c11a478865229840e87e4c96ea3f439101f31a5d35f75f

# Stage 1: build the wheels that need a compiler (pycairo, for the PDF export)
FROM ${PYTHON_IMAGE} AS build
RUN apt-get update \
 && apt-get install -y --no-install-recommends gcc pkg-config libcairo2-dev \
 && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# Stage 2: Caddy, the static front server (a single static binary)
FROM ${CADDY_IMAGE} AS caddy

# Stage 3: the runtime image, without the compiler toolchain
FROM ${PYTHON_IMAGE}
RUN apt-get update \
 && apt-get install -y --no-install-recommends libcairo2 \
 && rm -rf /var/lib/apt/lists/* \
 && useradd --create-home --uid 1000 app
COPY --from=caddy /usr/bin/caddy /usr/local/bin/caddy
WORKDIR /app
COPY --from=build /wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels
COPY --chown=app:app . .

ENV PYTHONUNBUFFERED=1 \
    DATA_DIR=/data \
    SITE_DIR=/data/site \
    SCREENSHOTS_ENABLED=false \
    PORT=8080 \
    APP_PORT=8501 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=127.0.0.1 \
    STREAMLIT_SERVER_BASE_URL_PATH=app \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    XDG_DATA_HOME=/data/caddy \
    XDG_CONFIG_HOME=/data/caddy-config
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/app/_stcore/health', timeout=4)"
CMD ["sh", "scripts/start.sh"]
