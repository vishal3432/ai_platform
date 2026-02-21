# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies first (Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Expose port
EXPOSE 8000

# Run the app using Daphne (ASGI server for WebSocket support)
CMD ["python", "-m", "daphne", "-b", "0.0.0.0", "-p", "8000", "core.asgi:application"]
