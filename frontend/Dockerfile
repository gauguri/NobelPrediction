FROM node:18-alpine

WORKDIR /usr/src/app
COPY package.json ./
RUN npm install -g pnpm && pnpm install

COPY . .
EXPOSE 5173
CMD ["pnpm", "dev", "--host", "0.0.0.0", "--port", "5173"]
