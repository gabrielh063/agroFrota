FROM node:22-alpine AS build
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY frontend/ ./
ARG VITE_API_URL=
ARG VITE_TENANT_DATABASE=agrofrota_tenant
ENV VITE_API_URL=${VITE_API_URL} VITE_TENANT_DATABASE=${VITE_TENANT_DATABASE}
RUN npm run build

FROM nginx:1.27-alpine
COPY deploy/persistent/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist/ /usr/share/nginx/html/
EXPOSE 8088
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD wget -q -O /dev/null http://127.0.0.1:8088/api/health || exit 1
