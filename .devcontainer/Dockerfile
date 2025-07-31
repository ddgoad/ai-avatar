# AI Avatar Development Container
# Optimized for Azure AI Services, Text-to-Speech Avatar, Flask, and Python
FROM mcr.microsoft.com/devcontainers/python:3.11-bullseye

# Install system dependencies for AI/ML, web development, and Azure AI Services
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
        # Audio/Video processing for AI Avatar
        ffmpeg \
        libavcodec-extra \
        # Web development dependencies for Flask
        libnss3-dev \
        libatk-bridge2.0-dev \
        libdrm-dev \
        libxkbcommon-dev \
        libgtk-3-dev \
        libgbm-dev \
        libasound2-dev \
        # AI/ML system dependencies
        libgl1-mesa-glx \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender-dev \
        libgomp1 \
        # Additional development utilities
        curl \
        wget \
        git \
        build-essential \
        # For handling certificates and SSL
        ca-certificates \
        gnupg \
        lsb-release \
        # For Azure AI Services and web development
        libssl-dev \
        libffi-dev \
        # Database clients (optional for session storage)
        sqlite3 \
        libsqlite3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for AI Avatar development
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    FLASK_ENV=development \
    FLASK_DEBUG=1

# Set working directory
WORKDIR /workspace

# Upgrade pip and install essential Python tools
RUN python -m pip install --upgrade pip setuptools wheel

# Set the default shell to bash
SHELL ["/bin/bash", "-c"]