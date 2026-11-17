# Stage 0: build the React app
FROM node:24 AS build-stage

WORKDIR /app

COPY package*.json /app/
RUN npm ci

COPY ./ /app/

# Empty = call the API on the same domain the app is served from (/api/v1/...)
ARG VITE_API_URL=""
ENV VITE_API_URL=${VITE_API_URL}

RUN npm run build


# Stage 1: Caddy serves the built files, proxies the API and handles HTTPS
FROM caddy:2

COPY --from=build-stage /app/dist/ /srv
COPY ./Caddyfile /etc/caddy/Caddyfile
