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

## Repo structure

```text
scripts/
  startup-script.sh          # DigitalOcean user-data bootstrap
  install-training-stack.sh  # HF diffusers LoRA training setup
research/
  project-brief.md           # hackathon plan and architecture
  research-log.md            # infrastructure research and findings
  amd-diffusion-models-course-notes.md
training/
  datasets/                  # image sets for LoRA training (gitignored)
  outputs/                   # trained LoRA artifacts (gitignored)
  logs/                      # training logs
internal/
  AMD Feedback.md            # platform feedback (not in git)
outputs/                     # generated images (gitignored)
```

## Use the ComfyUI API

ComfyUI generation uses:

```bash
POST http://127.0.0.1:8188/prompt
```

## Training LoRA on AMD MI300X

After the droplet boots:

```bash
# SSH in and install the training stack
/root/nemoflix/scripts/install-training-stack.sh
```

This installs Hugging Face `diffusers` and sets up the training workspace at `/root/nemoflix-training/`.

### Run training

```bash
cd /root/nemoflix-training
./train-lora-sdxl.sh datasets/sample my-lora
```

Copy the resulting `.safetensors` to `/root/ComfyUI/models/loras/` and use it in ComfyUI.

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