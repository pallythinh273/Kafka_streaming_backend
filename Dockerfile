# using python 3.9 slim image
FROM python:3.9-slim
WORKDIR /app

COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app/

# Set environment variables
ENV PYTHONUNBUFFERED=1

# ENV PYTHONDONTWRITEBYTECODE=1
# RUN python manage.py collectstatic --no-input
# RUN python manage.py migrate

# CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "weather.asgi:application"]
# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "weather_visualization.wsgi:application"]