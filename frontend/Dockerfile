# ==============================================================================
# NWIS (Nearby Wells Intelligence System) - Frontend Dockerfile
# ==============================================================================
# Multi-stage build: 
#   Stage 1: Build the React + Vite application
#   Stage 2: Serve production bundle with Nginx reverse proxy
# ==============================================================================

FROM node:20-alpine AS builder

WORKDIR /app

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# Stage 2: Production Nginx Server
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
