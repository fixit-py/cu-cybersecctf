FROM node:18-alpine

WORKDIR /app

COPY package.json package-lock.json* ./

# dependencies
RUN npm install

COPY . .

EXPOSE 3000

CMD ["node", "server.js"]
