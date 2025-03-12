FROM node:18-alpine

WORKDIR /app

# Copy only production dependencies and pre-built assets
COPY package.json package-lock.json* ./
COPY .next ./.next
COPY public ./public
COPY next.config.ts ./

# Install only production dependencies
RUN npm ci --only=production

ENV NODE_ENV=production
ENV PORT=3000

EXPOSE 3000
CMD ["npm", "start"]