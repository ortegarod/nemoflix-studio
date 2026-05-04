# AMD Hackathon Project Brief

## Working Title
Agent-Native LoRA Studio for AMD GPUs

## One-Liner
Bring your own AI agent, train a model with your photos on AMD Cloud GPU, then generate images and videos through that agent.

## Core Pitch
This project shows the full AMD stack in one clean demo:
- **Fine-tuning on AMD GPUs** via LoRA training (get model from HuggingFace)
- **Inference on AMD GPUs** via ComfyUI + ROCm
- **Agentic workflow** where a user talks to an AI agent instead of hand-driving the image pipeline

The goal is: **an AI agent can train, manage, and use a custom LoRA on AMD infrastructure with ComfyUI.**

---

## User Story
A creator uploads a small image set.
The system trains a LoRA on AMD MI300X.
Then the creator talks to an AI agent:
- “Give me a photo where I am at the beach laughing and having a good time.”

The agent turns that request into a ComfyUI workflow and returns finished images.

---

## MVP

### 1. AMD setup
- automated droplet bootstrap
- ROCm + PyTorch + ComfyUI working
- documented setup flow

### 2. LoRA training on MI300X
- train on a small curated dataset
- save trained LoRA artifact
- document training time and AMD-specific settings

### 3. Inference with trained LoRA
- ComfyUI workflow using the LoRA
- generate images successfully on MI300X
- save outputs to a gallery/output folder

### 4. Agent interface
- use the provided API from any compatible AI agent
- user gives natural language request
- agent selects workflow inputs and triggers generation

### 5. Demoable result
- before: generic base model output
- after: output using trained LoRA
- clear visual proof of training impact

### 6. API
- health endpoint
- train endpoint
- generate endpoint
- agent-friendly docs

### Web UI
A simple frontend for:
- upload dataset
- trigger training
- submit prompts
- view generated images
- see job status

### Judge Self-Hosting Path
- clone repo
- run one setup command
- start services
- use sample dataset and prompt

---

## Recommended Architecture

### Setup Layer
- startup/bootstrap script for AMD droplet
- ComfyUI as systemd service
- optional training service/process

### Training Layer
- LoRA training script or service
- input dataset folder
- output LoRA artifact folder
- training config presets for AMD

### Inference Layer (ComfyUI)
- ComfyUI workflow
- LoRA injection into workflow

---

## Judge Demo Flow

1. Upload sample curated dataset
2. Start LoRA training on MI300X
3. Show progress/logs briefly
4. Use resulting LoRA in live generation
5. Prompt through agent, not raw ComfyUI
6. Show that the same system is reusable by any agent

---

## What To Measure
- setup time on AMD droplet
- LoRA training time
- image generation latency
- VRAM usage
- total artifact sizes
- differences between base output and LoRA output

---

## Recommended Build Order

### Phase 1: infrastructure proof
- bootstrap script
- ComfyUI service
- test generation

### Phase 2: training proof
- train one LoRA on MI300X
- save and validate artifact

### Phase 3: agent workflow
- natural language prompt in
- image out

### Phase 4: polish
- web UI
- docs
- demo script

---

## Recommended Positioning

**An AI agent-native visual fine-tuning and image/video generation stack for AMD GPUs.**

---

## Recommendation
The winning path is a focused repo that proves:
- AMD setup works
- LoRA training works
- agent-triggered generation works