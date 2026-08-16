# Use a small Python image.
FROM python:3.13-slim

# All commands inside the container
# will run from this folder.
WORKDIR /app

# Prevent Python from creating .pyc files
# and make logs appear immediately.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Upgrade pip.
RUN pip install --upgrade pip

# Copy the project into the container.
COPY . .

# Install dependencies from pyproject.toml.
RUN pip install --no-cache-dir .

# FastAPI will run on port 8000.
EXPOSE 8000

# Start the FastAPI application.
CMD ["python", "-m", "uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]