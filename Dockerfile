# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install necessary dependencies for Chrome and ChromeDriver
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    gnupg2 \
    ca-certificates \
    lsb-release \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libdbus-1-3 \
    libgdk-pixbuf2.0-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    --no-install-recommends

# Install Google Chrome
RUN curl -sSL https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -o google-chrome.deb
RUN dpkg -i google-chrome.deb || apt-get install -y -f
RUN apt-get install -f

# Install ChromeDriver (latest version)
RUN LATEST=$(curl -sSL https://chromedriver.storage.googleapis.com/LATEST_RELEASE) \
    && wget https://chromedriver.storage.googleapis.com/$LATEST/chromedriver_linux64.zip \
    && unzip chromedriver_linux64.zip -d /usr/local/bin/

# Set the DISPLAY environment variable for headless operation
ENV DISPLAY=:99

# Copy the requirements file and install Python dependencies
COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt

# Set the working directory
WORKDIR /app

# Copy the rest of the application code
COPY . /app/

# Run the application using Gunicorn
#CMD ["gunicorn", "app:app"]
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]





