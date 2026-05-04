# AMD Developer Hackathon — Research Log

**Date:** 2026-04-28  
**Status:** Pre-hackathon infrastructure research and setup  
**Credits:** $100 AMD Developer Cloud (~50 hours MI300X)  
**Goal:** Validate ComfyUI + LoRA training on AMD ROCm

---

## 1. Hackathon Details

**Event:** AMD Developer Hackathon (lablab.ai)  
**Dates:** May 4–10, 2026  
**Kickoff:** Monday, May 4, 11:00 AM CDT  
**Submission Deadline:** Saturday, May 10, 2:00 PM CDT  
**Registration:** Enrolled. Credits active.  
**On-site:** SF (May 9-10), invite-only — we are online-only.

### Tracks
| Track | Focus | Tech Stack | Best For |
|-------|-------|-----------|----------|
| 1 | AI Agents & Agentic Workflows | LangChain, CrewAI, AutoGen + open-source models | Beginners |
| 2 | Fine-Tuning on AMD GPUs | ROCm, PyTorch, HuggingFace, vLLM | Advanced/GPU-intensive |
| 3 | Vision & Multimodal AI | Llama 3.2 Vision, Qwen-VL | Images, video, audio |
| Extra | Ship It + Build in Public | Social updates, ROCm feedback, open-source | Any track |

### Prizes
- **Grand Prize:** $5,000
- **Track 1st/2nd/3rd:** $2,500 / $1,500 / $1,000 each
- **Hugging Face:** Reachy Mini robot + HF PRO credits (most-liked Space)
- **Total Pool:** $21,500+ cash + AMD Radeon AI PRO R9700 GPU

**Pre-hackathon setup explicitly encouraged by organizers:**  
> "Get a head start on your project by using the resources on lablab.ai!"

---

## 2. AMD MI300X GPU Droplet Specs

| Spec | Value |
|------|-------|
| GPU | 1x AMD Instinct MI300X |
| VRAM | 192 GB |
| vCPU | 20 |
| RAM | 240 GB |
| Boot Disk | 720 GB NVMe SSD |
| Scratch Disk | 5 TB NVMe SSD |
| Price | $1.99/GPU/hr |
| ROCm | 7.2 (via ROCm™ Software image) |
| OS Options | Ubuntu 24.04, 22.04, bare OS |

**Image Selected:** ROCm™ Software 7.2 (Ubuntu 24.04 base)  
**Why:** ROCm pre-installed, latest version, not locked into specific framework

---

## 3. ComfyUI + ROCm Compatibility Research

### Official Support Status
- **Jan 2026:** Official AMD ROCm support launched for ComfyUI **Windows** (Desktop/Portable/Git)
- **Linux ROCm:** Supported via community and upstream, less polished than Windows path
- **ComfyUI docs:** "Supports all system types and GPU types (Nvidia, AMD, Intel, Apple Silicon)"

### Key Findings
- ROCm 7.2 is the latest, matches ComfyUI's recent Windows support launch
- **MI300X is datacenter Instinct GPU**, not consumer Radeon — ROCm optimized for compute/ML
- **Risk:** Custom nodes with CUDA-only compiled extensions may fail (FaceDetailer, some video nodes)
- **Approach:** Install ComfyUI core first, test basic image generation, THEN add custom nodes one by one

### Sources
- ComfyUI Official Docs: https://docs.comfy.org/installation/system_requirements
- AMD ROCm Blog Post: https://blog.comfy.org/p/official-amd-rocm-support-arrives
- Reddit r/ROCm discussion on ROCm 7.2.2
- AMD ROCm ComfyUI Guide: https://rocm.docs.amd.com

---

## 4. PyTorch + ROCm Versions

| ROCm Version | PyTorch Wheel URL | Notes |
|-------------|---------------------|-------|
| 7.2 | `https://download.pytorch.org/whl/rocm7.2` | Ideal, may not have wheels yet |
| 7.0 | `https://download.pytorch.org/whl/rocm7.0` | Fallback |
| 6.2 | `https://download.pytorch.org/whl/rocm6.2` | Last resort fallback |

**Strategy in startup script:** Try 7.2 → 7.0 → 6.2 with fallbacks

---

## 5. SSH Access

Use a dedicated SSH key for the AMD Cloud droplet. Keep private keys and provider-specific credentials outside the repository.

---

## 6. Startup Script

**Location:** `~/amd-hackathon/scripts/startup-script.sh`  
**Approach:** Bare bones, no firewall, no custom nodes, no helper scripts

What it does:
1. `apt update` + install `git`, `python3-pip`, `htop`
2. Verify GPU with `rocm-smi` and `rocminfo`
3. Install PyTorch for ROCm (7.2 → 7.0 → 6.2 fallback)
4. Clone ComfyUI from official repo
5. Install ComfyUI-Manager for proper model management
6. Install core requirements
7. Copy official example script for testing
8. Download SD 1.5 model as **smoke test** (4GB, fast, official example compatible)

**Why SD 1.5:** It's the model in ComfyUI's official `basic_api_example.py`. No config changes needed. This is infrastructure verification, not content.

**Explicitly NOT included:**
- Firewall rules
- Custom user creation
- Custom nodes (install manually after core works)
- Helper scripts

---

## 7. ComfyUI API Approach

**Official API exists** — ComfyUI exposes HTTP endpoints (`/prompt`, `/history`, `/queue`, `/upload/image`, etc.) and WebSocket (`/ws`).

**Official examples exist** in the ComfyUI repository:
- `basic_api_example.py` — sync HTTP with `urllib.request`
- `websockets_api_example.py` — sync WS with `websocket-client`

**Potential API approach:** A small async wrapper can call the same official API using `httpx.AsyncClient`.

**For this test:** Official sync examples are fine. We just need to verify ComfyUI generates an image.

---

## 8. Model Management

**ComfyUI-Manager** is the proper tool for model downloads. It knows the right directories and handles metadata.

**Why wget for the test model:**
- Manager API requires ComfyUI to be **running**
- Startup script runs during first boot, before ComfyUI starts
- wget gets us a test model immediately for smoke testing
- Once ComfyUI is running, Manager handles everything else

---

## 9. Next Steps

1. **Create droplet** with ROCm™ Software 7.2 image + startup script
2. **Wait for setup** (time unknown)
3. **SSH in** and verify: `rocm-smi`, PyTorch GPU detection, ComfyUI core
4. **Start ComfyUI** and run official example to test basic generation
5. **Document what works** for hackathon planning

---

## 10. Open Questions

- Will Wan 2.2 I2V video generation work? (need specific custom nodes)
- Can we run kohya_ss or AI-Toolkit for LoRA training on ROCm?