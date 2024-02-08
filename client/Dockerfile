FROM node:16-alpine AS build

WORKDIR /frontend


COPY package*.json ./


RUN npm install

COPY . ./
RUN chmod +x node_modules/.bin/react-scripts
# Build the React application
RUN npm run build

# Install serve
RUN npm install -g serve

# Use Node.js to serve the React app
FROM node:16-alpine

# Copy the build output
COPY --from=build /frontend/build /frontend/build
# Copy node_modules folder
COPY --from=build /frontend/node_modules /frontend/node_modules

# Expose port 5000 (or any other port you prefer)n
EXPOSE 5000


# Start the React app using serve
CMD ["/frontend/node_modules/.bin/serve", "-s", "/frontend/build", "-l", "5000"]