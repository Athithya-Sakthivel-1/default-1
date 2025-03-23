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

# Resolve SSH configuration conflict automatically
echo "1" | sudo dpkg --force-confnew --configure -a

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
    openssh-server unzip

curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
rm -rf awscliv2.zip aws/


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

# Ensure correct package directory exists
PACKAGE_DIR="$PROJECT_ROOT/src/fraud_detection_system"
if [ ! -d "$PACKAGE_DIR" ]; then
    echo "Creating missing package directory: $PACKAGE_DIR"
    mkdir -p "$PACKAGE_DIR"
    touch "$PACKAGE_DIR/__init__.py"
fi

# Ensure `pyproject.toml` exists at the correct location
if [ ! -f "$PROJECT_ROOT/pyproject.toml" ]; then
    echo "Creating default Poetry project..."
    poetry init --no-interaction --name "fraud-detection-system"
fi

# Install project dependencies
echo "Installing project dependencies..."
poetry install --no-interaction
pip install --quiet bentoml docker kubernetes boto3

# Clean up unused packages
echo "Cleaning up unused packages..."
sudo apt autoremove -y

echo -e "\ncd fraud_detection_system\nsource .venv/bin/activate" >> ~/.bashrc
source ~/.bashrc


echo "Setup complete. System is ready."
