FROM node:24-bookworm-slim AS web
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim
WORKDIR /app
ENV OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMBA_NUM_THREADS=1
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 && rm -rf /var/lib/apt/lists/*
COPY requirements.txt requirements-ensemble.txt ./
RUN pip install --no-cache-dir -r requirements-ensemble.txt
COPY backend/ backend/
COPY ml/ ml/
COPY models/ models/
COPY data/processed/ data/processed/
COPY scripts/ scripts/
COPY --from=web /app/frontend/dist frontend/dist
EXPOSE 8000
CMD ["sh", "-c", "exec python -m uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000} --no-access-log"]
