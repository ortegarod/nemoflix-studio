#!/bin/bash
set -x
exec > >(tee -a /var/log/setup.log) 2>&1

echo "=== AMD MI300X Setup Starting ==="

# Basic tools
apt-get update -y
apt-get install -y git python3-pip python3-venv htop wget curl

# Verify GPU
echo "=== GPU Check ==="
/opt/rocm/bin/rocm-smi
/opt/rocm/bin/rocminfo | head -20

# Create virtual environment

echo "=== Creating Python venv ==="
python3 -m venv /root/comfyui-venv
source /root/comfyui-venv/bin/activate

# Install PyTorch for ROCm inside venv
echo "=== Installing PyTorch for ROCm ==="
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm7.2 2>/dev/null || \
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm7.0 2>/dev/null || \
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm6.2

# Verify PyTorch sees the GPU
python3 -c "import torch; print('PyTorch:', torch.__version__); print('ROCm:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"

# Install ComfyUI
echo "=== Installing ComfyUI ==="
cd /root
git clone https://github.com/comfyanonymous/ComfyUI.git

# Install ComfyUI-Manager
cd /root/ComfyUI/custom_nodes
git clone https://github.com/ltdrdata/ComfyUI-Manager.git
cd /root/ComfyUI

# Install requirements inside venv
pip install -r requirements.txt
if [ -f /root/ComfyUI/custom_nodes/ComfyUI-Manager/requirements.txt ]; then
    pip install -r /root/ComfyUI/custom_nodes/ComfyUI-Manager/requirements.txt
fi

# Copy official example for testing
cp /root/ComfyUI/script_examples/basic_api_example.py /root/test_comfyui.py

# Download test model before starting service
mkdir -p /root/ComfyUI/models/checkpoints
cd /root/ComfyUI/models/checkpoints
wget -q --show-progress "https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors" -O v1-5-pruned-emaonly.safetensors || echo "WARNING: Model download failed"

# Create ComfyUI systemd service
cat > /etc/systemd/system/comfyui.service << 'EOF'
[Unit]
Description=ComfyUI
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/ComfyUI
Environment="PATH=/root/comfyui-venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=/root/comfyui-venv/bin/python /root/ComfyUI/main.py --listen 0.0.0.0 --port 8188
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable comfyui.service
systemctl start comfyui.service

# Show service status in log
systemctl --no-pager --full status comfyui.service || true

echo "=== Setup Complete ==="
echo "ComfyUI service: systemctl status comfyui"
echo "Logs: journalctl -u comfyui -n 100 --no-pager"
echo "Local API health: curl http://127.0.0.1:8188/system_stats"
echo "Test script: source /root/comfyui-venv/bin/activate && python /root/test_comfyui.py"
