FROM node:20-slim

WORKDIR /app

# Install deps from apps/admin/ context
COPY apps/admin/package.json apps/admin/package-lock.json* ./
RUN npm install --legacy-peer-deps 2>/dev/null || npm install --legacy-peer-deps

# Copy admin source (volume mount overrides in dev via compose)
COPY apps/admin/ ./

EXPOSE 5173

# Dev mode with hot-reload bound to all interfaces
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
