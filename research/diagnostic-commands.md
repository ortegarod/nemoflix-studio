# AMD MI300X Droplet — Diagnostic Commands

**How to check what happened after the droplet boots and the startup script runs.**

---

## 1. SSH into the Droplet

From any terminal:
```bash
ssh -i ~/.ssh/id_ed25519_amd_hackathon root@<droplet-ip>
```

Replace `<droplet-ip>` with the actual IP address from DigitalOcean.

---

## 2. Check the Startup Script Log

This shows everything the script did (or failed to do):
```bash
cat /var/log/setup.log
```

---

## 3. Check GPU Status

```bash
/opt/rocm/bin/rocm-smi
```

Also check:
```bash
/opt/rocm/bin/rocminfo | head -30
```

---

## 4. Check if PyTorch Sees the GPU

Activate the virtual environment first, then test:
```bash
source /root/comfyui-venv/bin/activate
python3 -c "import torch; print('PyTorch:', torch.__version__); print('GPU detected:', torch.cuda.is_available()); print('GPU name:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"
```

**Expected output:**
```
PyTorch: 2.x.x+rocm7.x
GPU detected: True
GPU name: AMD Instinct MI300X
```

**If `GPU detected: False`:** PyTorch installed but can't talk to ROCm. Check `rocm-smi` first.

---

## 5. Check if ComfyUI Installed

```bash
ls -la /root/ComfyUI/
```

**Should see:** `main.py`, `requirements.txt`, `models/`, `custom_nodes/`, etc.

Check if ComfyUI-Manager is there:
```bash
ls -la /root/ComfyUI/custom_nodes/ComfyUI-Manager/
```

---

## 6. Check if the Test Model Downloaded

```bash
ls -la /root/ComfyUI/models/checkpoints/
```

**Should see:** `v1-5-pruned-emaonly.safetensors` (~4GB)

If missing, download manually:
```bash
cd /root/ComfyUI/models/checkpoints
wget "https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors"
```

---

## 7. Check What's Currently Running

```bash
ps aux | grep -E "(python|wget|git|rocm)" | grep -v grep
```

Shows if ComfyUI is running, if downloads are still happening, etc.

---

## 8. Start ComfyUI and Test

```bash
# Activate the virtual environment
source /root/comfyui-venv/bin/activate

# Start ComfyUI
cd /root/ComfyUI
python main.py --listen 0.0.0.0 --port 8188
```

**In a second terminal (or after ComfyUI finishes loading):**
```bash
ssh -i ~/.ssh/id_ed25519_amd_hackathon root@<droplet-ip>
cd /root
source /root/comfyui-venv/bin/activate
python test_comfyui.py
```

**Check for the output image:**
```bash
ls -la /root/ComfyUI/output/
```
