# Builder stage with memory optimizations
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files first for better caching
COPY package*.json ./
RUN npm install

# Copy only necessary files
COPY next.config.ts ./
COPY tsconfig.json ./
COPY postcss.config.js ./
COPY public ./public
COPY src ./src

# Build with NODE_OPTIONS to limit memory usage
ENV NODE_OPTIONS="--max_old_space_size=2048"
RUN npm run build

# Runner stage
FROM node:18-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV PORT=3000

# Copy only the necessary files from the builder stage
COPY --from=builder /app/next.config.ts ./
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

EXPOSE 3000
CMD ["npm", "start"]