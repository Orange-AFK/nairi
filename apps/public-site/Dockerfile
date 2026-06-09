FROM node:20-slim

WORKDIR /app

# Install deps from apps/public-site/ context
COPY apps/public-site/package.json apps/public-site/package-lock.json* ./
RUN npm install --legacy-peer-deps 2>/dev/null || npm install --legacy-peer-deps

# Copy public-site source (volume mount overrides in dev via compose)
COPY apps/public-site/ ./

EXPOSE 3000

# Dev mode with hot-reload bound to all interfaces
CMD ["npm", "run", "dev", "--", "-H", "0.0.0.0"]
