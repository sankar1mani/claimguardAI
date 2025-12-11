# ClaimGuard AI - Frontend Dockerfile
# React + Vite application

FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files first for better caching
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm install

# Copy application code
COPY . .

# Expose Vite dev server port
EXPOSE 5173

# Command to run Vite dev server with host flag for Docker
CMD ["npm", "run", "dev", "--", "--host"]
