# Multi-stage Alpine Caddy container for career.masrisystems.com
FROM python:3.11-alpine AS builder

WORKDIR /build
COPY . /build

# Build the starter kit bundle during container image compilation
RUN python scripts/bundle_starter_kit.py

# Final runtime stage
FROM caddy:2-alpine

WORKDIR /usr/share/caddy

# Copy static assets and built download package
COPY index.html ./index.html
COPY resume.html ./resume.html
COPY resume.js ./resume.js
COPY download.html ./download.html
COPY style.css ./style.css
COPY hub.js ./hub.js
COPY config ./config
COPY alex-morgan-profile.webp ./alex-morgan-profile.webp
COPY stefan-kramer-profile.webp ./stefan-kramer-profile.webp
COPY robots.txt ./robots.txt
COPY jobs/roles ./jobs/roles
COPY --from=builder /build/download/resume-template-starter.zip ./download/resume-template-starter.zip

# Copy Caddyfile configuration
COPY Caddyfile /etc/caddy/Caddyfile

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD wget -q -O /dev/null http://127.0.0.1:80/ || exit 1
