FROM node:24-bookworm-slim AS web
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
COPY models/metadata.json /app/models/metadata.json
COPY data/processed/reviewer_samples_v2.json /app/data/processed/reviewer_samples_v2.json
RUN npm run build

FROM python:3.11-slim
WORKDIR /app
COPY --from=web /app/frontend/dist frontend/dist
ENV OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMBA_NUM_THREADS=1
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 && rm -rf /var/lib/apt/lists/*
COPY requirements.txt requirements-ensemble.txt ./
RUN pip install --no-cache-dir --no-compile -r requirements-ensemble.txt
COPY backend/ backend/
COPY ml/ ml/
COPY models/ models/
COPY data/processed/ data/processed/
COPY scripts/ scripts/
EXPOSE 8000
CMD ["sh", "-c", "exec python -m uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000} --no-access-log"]
