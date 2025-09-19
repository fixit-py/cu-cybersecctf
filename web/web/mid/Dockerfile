FROM node:18-alpine

WORKDIR /app

COPY package.json package-lock.json* ./

# dependencies
RUN npm install

COPY . .

# Build
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
