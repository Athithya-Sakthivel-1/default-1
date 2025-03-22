#!/bin/bash

set -e  # Exit if any command fails

echo "Starting automated setup..."

# Ensure script is executed from the correct directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

# Update system & install required packages
echo "Updating system and installing dependencies..."
sudo apt update -y && sudo apt install -y --no-install-recommends \
    python3.11 python3.11-venv python3.11-dev python3-pip \
    build-essential libssl-dev libffi-dev \
    libpq-dev libcurl4-openssl-dev \
    graphviz libgraphviz-dev \
    docker.io containerd software-properties-common gpg curl

# Install Kubectl if not installed
if ! command -v kubectl &>/dev/null; then
    echo "Installing Kubectl..."
    sudo curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.31/deb/Release.key | sudo gpg --dearmor -o /usr/share/keyrings/kubernetes-archive-keyring.gpg
    echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.31/deb/ /" | sudo tee /etc/apt/sources.list.d/kubernetes.list
    sudo apt update -y && sudo apt install -y kubectl
else
    echo "Kubectl is already installed. Skipping..."
fi

# Install K3s if not installed
if ! command -v k3s &>/dev/null; then
    echo "Installing K3s..."
    curl -sfL https://get.k3s.io | sh -
else
    echo "K3s is already installed. Skipping..."
fi

# Install Poetry if not installed
if ! command -v poetry &>/dev/null; then
    echo "Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 - --quiet
    export PATH="$HOME/.local/bin:$PATH"
else
    echo "Poetry is already installed. Skipping..."
fi

# Configure Poetry
poetry config virtualenvs.in-project true
poetry env use python3.11 || true  # Avoid breaking if already configured

# Ensure pyproject.toml exists at the ROOT directory
if [ ! -f "pyproject.toml" ]; then
    echo "pyproject.toml not found in root. Creating default project..."
    poetry init --no-interaction --name "fraud-detection-system"
fi

# Install dependencies & project
echo "Installing project dependencies..."
poetry install --no-interaction --quiet
pip install --quiet bentoml docker kubernetes

# Clean up unused packages
echo "Cleaning up unused packages..."
sudo apt autoremove -y

echo "Setup complete. System is ready."
