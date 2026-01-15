FROM node:18-alpine
WORKDIR /app
RUN npm install --production
COPY . .
CMD ["node", "server.js"]
EXPOSE 3000