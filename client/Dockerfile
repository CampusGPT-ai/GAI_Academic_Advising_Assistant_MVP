FROM --platform=linux/amd64 node:16-alpine AS build

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . ./


# Build the React application
RUN npm run build

FROM nginx

COPY ./nginx/nginx.conf /etc/nginx/nginx.conf
COPY --from=build /app/build /usr/share/nginx/html

COPY .env /usr/share/nginx
COPY inject-env.sh /usr/share/nginx
COPY entrypoint.sh /usr/share/nginx


RUN chmod +x /usr/share/nginx/inject-env.sh /usr/share/nginx/entrypoint.sh

# Expose port 5000 (or any other port you prefer)n
EXPOSE 80

ENTRYPOINT ["/usr/share/nginx/entrypoint.sh"]