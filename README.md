# Nemoflix

AI Agent-native image and video generation on AMD GPUs using ComfyUI.

This repo currently bootstraps ComfyUI on a DigitalOcean AMD MI300X ROCm 7.2 GPU Droplet. ComfyUI's HTTP API is the working generation interface.

## Startup script

```bash
scripts/startup-script.sh
```

Use this as DigitalOcean user data on a **ROCm 7.2 Software** GPU Droplet.

The script:

- installs host packages and logs to `/var/log/setup.log`
- verifies ROCm/GPU visibility
- creates `/root/comfyui-venv`
- installs PyTorch ROCm
- clones this repo to `/root/nemoflix`
- installs ComfyUI + ComfyUI-Manager
- downloads the SD 1.5 test checkpoint
- starts `comfyui.service` on port `8188`
- queues one test image through ComfyUI's API

## Check setup

```bash
cloud-init status --long
tail -n 200 /var/log/setup.log
systemctl --no-pager --full status comfyui.service
curl -sS http://127.0.0.1:8188/system_stats
```

Outputs land in:

```bash
/root/ComfyUI/output/
```

## Use the ComfyUI API

ComfyUI generation uses:

```bash
POST http://127.0.0.1:8188/prompt
```

The installed example lives at:

```bash
/root/test_comfyui.py
```

Minimal curl pattern:

```bash
curl -sS -X POST http://127.0.0.1:8188/prompt \
  -H "Content-Type: application/json" \
  --data-binary @workflow.json
```

`workflow.json` is ComfyUI's exported API workflow format. The current test workflow is based on ComfyUI's own example at:

```bash
/root/ComfyUI/script_examples/basic_api_example.py
```