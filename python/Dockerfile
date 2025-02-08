FROM python:3.11-slim AS builder

WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY ./app ./app

# Set the working directory to the app folder and start FastAPI
WORKDIR /app
CMD ["python", "app/main.py"]
