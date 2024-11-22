# Start Generation Here
FROM node:16-slim

# Set the working directory
WORKDIR /app

# Install global dependencies
RUN npm install -g react-scripts sass

# Copy package files first
COPY package*.json ./

# Clean install dependencies
RUN npm ci --legacy-peer-deps

# Set environment variables
ENV NODE_ENV=development
ENV REACT_APP_API_URL=http://localhost:8080
ENV PORT=3001

# Copy the rest of the application
COPY . .

# Start the app
CMD ["npm", "start"]
# End Generation Here
