#!/bin/bash

set -e  # Exit on failure

echo "Starting automated setup..."

# Dynamically detect the project root (assumes this script is inside the repo)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT" || exit 1
echo "Detected project root: $PROJECT_ROOT"

# Prevent interactive prompts
export DEBIAN_FRONTEND=noninteractive
export DEBCONF_NONINTERACTIVE_SEEN=true

# Update system & install required packages
echo "Updating system and installing dependencies..."
sudo apt update -y && sudo apt upgrade -y

# Install Python 3.11 (fixed for Codespaces)
echo "Installing Python 3.11..."
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update -y && sudo apt install -y \
    python3.11 python3.11-venv python3.11-dev python3-pip

# Install essential dependencies
echo "Installing required libraries..."
sudo apt install -y --no-install-recommends \
    build-essential libssl-dev libffi-dev \
    libpq-dev libcurl4-openssl-dev \
    graphviz libgraphviz-dev \
    docker.io containerd software-properties-common gpg curl \
    openssh-server

# Install Kubectl if not installed
if ! command -v kubectl &>/dev/null; then
    echo "Installing Kubectl..."
    sudo curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.31/deb/Release.key | sudo gpg --dearmor -o /usr/share/keyrings/kubernetes-archive-keyring.gpg
    echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.31/deb/ /" | sudo tee /etc/apt/sources.list.d/kubernetes.list
    sudo apt update -y && sudo apt install -y kubectl
else
    echo "Kubectl is already installed. Skipping..."
fi

# Install K3s correctly in Codespaces
if ! command -v k3s &>/dev/null; then
    echo "Installing K3s..."
    curl -sfL https://get.k3s.io | sh -s - --write-kubeconfig-mode 644
    sudo service k3s start || true  # Avoid systemd issues
else
    echo "K3s is already installed. Skipping..."
fi

# Install Poetry correctly
if ! command -v poetry &>/dev/null; then
    echo "Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
else
    echo "Poetry is already installed. Skipping..."
fi

# Configure Poetry
poetry config virtualenvs.in-project true

# Ensure correct virtual environment usage
if [ ! -d "$PROJECT_ROOT/.venv" ]; then
    echo "Creating a virtual environment..."
    poetry env use python3.11 || true
fi

# Ensure pyproject.toml exists at the correct location
if [ ! -f "$PROJECT_ROOT/pyproject.toml" ]; then
    echo "Creating default Poetry project..."
    poetry init --no-interaction --name "fraud-detection-system"
fi

# Install project dependencies
echo "Installing project dependencies..."
poetry install --no-interaction
pip install --quiet bentoml docker kubernetes

# Clean up unused packages
echo "Cleaning up unused packages..."
sudo apt autoremove -y

# Ensure Docker is running
echo "Starting Docker..."
sudo service docker start || true

# Setup and start Neo4j
if [ "$(docker ps -aq -f name=neo4j)" ]; then
    echo "Neo4j container already exists. Restarting..."
    docker start neo4j || true
else
    echo "Starting new Neo4j container..."
    docker run --name neo4j -p 7474:7474 -p 7687:7687 -d -e NEO4J_AUTH=neo4j/password neo4j
fi

# Wait for Neo4j to initialize
echo "Waiting for Neo4j to initialize..."
sleep 10

# Test Neo4j connection
echo "Testing Neo4j connection..."
docker exec -i neo4j bin/cypher-shell -u neo4j -p password -d system "RETURN 'Neo4j is running' AS status;"

# Display Neo4j URL for Codespaces
if [ -n "$CODESPACE_NAME" ]; then
    echo "Neo4j Browser is available at: https://${CODESPACE_NAME}-7474.app.github.dev"
fi

echo "Setup complete. System is ready."
