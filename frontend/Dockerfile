# Build stage for the React app (ADR-3). Produces the production build at
# /app/dist. backend/Dockerfile embeds this build stage so the SPA is served
# by FastAPI in the single-container topology.
FROM node:22-alpine
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build