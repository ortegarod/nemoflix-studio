#!/bin/bash
set -Eeuo pipefail
set -x
exec > >(tee -a /var/log/setup.log) 2>&1

trap 'echo "ERROR: setup failed at line $LINENO"' ERR

APT_GET="apt-get -o DPkg::Lock::Timeout=300"
PYTHON_BIN="/root/comfyui-venv/bin/python"
APP_REPO_URL="https://github.com/ortegarod/nemoflix.git"
APP_DIR="/root/nemoflix"

echo "=== AMD MI300X ROCm 7.2 ComfyUI Setup Starting ==="

# Refresh package metadata before installing dependencies.
$APT_GET update -y

# Git is required to clone ComfyUI and ComfyUI-Manager.
$APT_GET install -y git

# Python tooling for an isolated host virtual environment.
$APT_GET install -y python3-pip
$APT_GET install -y python3.12-venv

# wget is required to download the test checkpoint.
$APT_GET install -y wget

# htop is optional, but useful for manual droplet debugging.
$APT_GET install -y htop

# curl is useful for local API health checks.
$APT_GET install -y curl

# Verify host GPU and ROCm visibility.
echo "=== Host GPU Check ==="
/opt/rocm/bin/rocm-smi
/opt/rocm/bin/rocminfo > /tmp/rocminfo.txt
head -20 /tmp/rocminfo.txt

# Create virtual environment on the host.
echo "=== Creating Python venv ==="
python3 -m venv /root/comfyui-venv
"$PYTHON_BIN" -m pip install --upgrade pip setuptools wheel

# Install PyTorch for ROCm inside venv.
# This is the slower path, but it is explicit and avoids DigitalOcean's Jupyter/Docker appliance behavior.
echo "=== Installing PyTorch for ROCm ==="
"$PYTHON_BIN" -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm7.2 || \
"$PYTHON_BIN" -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm7.0 || \
"$PYTHON_BIN" -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm6.2

# Verify PyTorch sees the GPU.
echo "=== PyTorch GPU Check ==="
"$PYTHON_BIN" -c "import torch; print('PyTorch:', torch.__version__); print('ROCm available:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"

# Clone the project repo. This is the application layer that will own future setup/runtime logic.
echo "=== Cloning Nemoflix repo ==="
git clone --depth 1 "$APP_REPO_URL" "$APP_DIR"

# Application install step intentionally comes later when the repo has a defined app entrypoint.
# Today this clone proves the deployment path includes our repository.

# Install ComfyUI.
echo "=== Installing ComfyUI ==="
cd /root
git clone https://github.com/comfyanonymous/ComfyUI.git

# Install ComfyUI-Manager.
git clone https://github.com/ltdrdata/ComfyUI-Manager.git /root/ComfyUI/custom_nodes/ComfyUI-Manager
cd /root/ComfyUI

# Install ComfyUI requirements inside venv.
"$PYTHON_BIN" -m pip install -r requirements.txt
"$PYTHON_BIN" -m pip install -r /root/ComfyUI/custom_nodes/ComfyUI-Manager/requirements.txt

# Copy official example for testing.
cp /root/ComfyUI/script_examples/basic_api_example.py /root/test_comfyui.py

# Download test model before starting service.
mkdir -p /root/ComfyUI/models/checkpoints
cd /root/ComfyUI/models/checkpoints
echo "Downloading SD 1.5 test checkpoint..."
wget -q "https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors" -O v1-5-pruned-emaonly.safetensors
test -s v1-5-pruned-emaonly.safetensors
ls -lh v1-5-pruned-emaonly.safetensors

# Create ComfyUI systemd service on the host.
cat > /etc/systemd/system/comfyui.service << EOF
[Unit]
Description=ComfyUI
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/ComfyUI
Environment="PATH=/root/comfyui-venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=$PYTHON_BIN /root/ComfyUI/main.py --listen 0.0.0.0 --port 8188
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable comfyui.service
systemctl start comfyui.service

# Show service status in log.
systemctl --no-pager --full status comfyui.service

# Verify API from the host.
echo "=== Waiting for ComfyUI API ==="
for i in {1..60}; do
    if curl -sS --max-time 5 http://127.0.0.1:8188/system_stats; then
        break
    fi
    echo "Waiting for ComfyUI API... ($i/60)"
    sleep 5
done
curl -sS --max-time 5 http://127.0.0.1:8188/system_stats

echo "=== Queueing ComfyUI test generation ==="
"$PYTHON_BIN" /root/test_comfyui.py

echo "=== Setup Complete ==="
