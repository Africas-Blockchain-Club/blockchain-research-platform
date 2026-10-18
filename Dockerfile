# Two stages: build the wheels that need a compiler (pycairo, for the PDF
# export), then copy them into a slim runtime image without the toolchain.
FROM python:3.12-slim AS build
RUN apt-get update \
 && apt-get install -y --no-install-recommends gcc pkg-config libcairo2-dev \
 && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

FROM python:3.12-slim
RUN apt-get update \
 && apt-get install -y --no-install-recommends libcairo2 \
 && rm -rf /var/lib/apt/lists/* \
 && useradd --create-home --uid 1000 app
WORKDIR /app
COPY --from=build /wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels
COPY --chown=app:app . .

ENV PYTHONUNBUFFERED=1 \
    DATA_DIR=/data \
    SCREENSHOTS_ENABLED=false \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_PORT=8080 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0
EXPOSE 8080
CMD ["sh", "scripts/start.sh"]
