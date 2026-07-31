FROM python:3.12-slim

WORKDIR /dualingo

COPY . .

RUN chmod -R 777 /dualingo/cookies

RUN chmod +x run.sh

# Install dependencies (combine apt-get update calls)
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libgbm1 \
    libgtk-3-0 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    xdg-utils

# Download and install Chrome
RUN curl -sSL https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -o chrome.deb \
    && apt-get install -y ./chrome.deb \
    && rm chrome.deb

# Install Python packages
RUN pip install selenium webdriver-manager

# Clean up
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Set timezone to Israel
ENV TZ=Asia/Jerusalem
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

CMD ["/dualingo/run.sh"]