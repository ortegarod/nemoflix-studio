# Nemoflix

Agent-native LoRA training and image generation on AMD GPUs.

## Current setup

This repo currently centers on the AMD droplet startup script:

```bash
scripts/startup-script.sh
```

The script is intended to run when initializing an AMD GPU droplet. It installs the base ComfyUI environment, ROCm PyTorch dependencies, ComfyUI-Manager, and a small test checkpoint for verifying generation.

