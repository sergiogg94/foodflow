# Multi-stage build (ADR-3): build the React frontend, then serve the static
# build from the FastAPI image. Build context is the repository root so this
# Dockerfile can copy frontend/ sources.
FROM node:22-alpine AS frontend-build
WORKDIR /build/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.13-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/app ./app
COPY --from=frontend-build /build/frontend/dist ./static
ENV FOODFLOW_STATIC_DIR=/app/static
ENV FOODFLOW_DB_PATH=/app/data/foodflow.db
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]