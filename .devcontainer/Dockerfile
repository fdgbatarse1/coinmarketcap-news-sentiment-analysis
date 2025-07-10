FROM pytorchlightning/pytorch_lightning:2.5.2-py3.12-torch2.7-cuda12.6.3

# Install necessary packages including Chrome for Selenium
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    ca-certificates \
    sudo \
    zsh \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
    
# Install Chrome
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get install ./google-chrome-stable_current_amd64.deb -y && \
    rm -f ./google-chrome-stable_current_amd64.deb

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.7.20 /uv /uvx /bin/

COPY requirements.in .
RUN uv pip compile requirements.in -o requirements.txt && \
    uv pip install --no-cache-dir -r requirements.txt --system

# User setup
ENV USERNAME=vscode \
    USER_UID=1000 \
    USER_GID=1000

RUN groupadd --gid $USER_GID $USERNAME && \
    useradd --create-home --shell /bin/bash --uid $USER_UID --gid $USER_GID $USERNAME && \
    echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME && \
    chmod 0440 /etc/sudoers.d/$USERNAME

# Set user and working directory
USER $USERNAME
WORKDIR /home/$USERNAME