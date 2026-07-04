FROM ghcr.io/actions/actions-runner:latest
USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    wget \
    gnupg \
    software-properties-common \
    python3 \
    python3-venv \
    python3-pip \
    fonts-liberation \
    libnss3 \
    libxss1 \
    libasound2 \
    libgtk-3-0 \
    libgbm1 \
    && rm -rf /var/lib/apt/lists/*

# Install Chromium + chromium-driver (arm64-native; Google Chrome/chromedriver
# have no official linux-arm64 build, so we use xtradeb's real .deb packages
# instead of Ubuntu's snap-based "chromium" transitional package)
RUN add-apt-repository -y ppa:xtradeb/apps \
    && apt-get update && apt-get install -y --no-install-recommends chromium chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Python venv and wheelhouse
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create working dir & add minimal scripts
WORKDIR /workspace
COPY requirements.txt /workspace/requirements.txt
# Install test deps into venv (this is done at build time; if builder has internet)
RUN /opt/venv/bin/pip install --no-cache-dir -r /workspace/requirements.txt

USER runner
