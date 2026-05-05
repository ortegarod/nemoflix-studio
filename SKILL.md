---
name: nemoflix-amd
description: Use Nemoflix to generate AI video through a simple HTTP API backed by ComfyUI on AMD GPU infrastructure. Use when an AI agent needs to upload an image, request text-to-video or image-to-video generation, check job status, or retrieve generated video outputs.
---

# Nemoflix AMD Skill

Nemoflix is an AI-agent-native video generation API. Agents call Nemoflix directly; humans may also use the HuggingFace Space UI, but the API is the primary interface.

## Backend

Set the API base URL:

```bash
export NEMOFLIX_API_URL="http://<backend-host>:8190"
```

For the AMD hackathon deployment, this points to the AMD GPU droplet running the Nemoflix API service beside ComfyUI.

## Check health

```bash
curl -sS "$NEMOFLIX_API_URL/api/health"
```

If health fails, do not pretend generation is available. Report that the backend is unavailable.

## Text-to-video

Use this when the user gives only a prompt.

```bash
curl -sS -X POST "$NEMOFLIX_API_URL/api/video/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "t2v",
    "prompt": "cinematic shot of a lone explorer walking across an alien desert",
    "width": 1280,
    "height": 720,
    "length": 121,
    "fps": 16
  }'
```

Response contains `prompt_id`. Save it and use it to check status.

## Image-to-video

First upload the source image:

```bash
curl -sS -X POST "$NEMOFLIX_API_URL/api/images/upload" \
  -F "file=@/path/to/source.png"
```

Use the returned `image` value in the generation request:

```bash
curl -sS -X POST "$NEMOFLIX_API_URL/api/video/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "i2v",
    "image": "source.png",
    "prompt": "cinematic shot, subject walking through neon rain, dramatic lighting",
    "width": 1280,
    "height": 720,
    "length": 121,
    "fps": 16
  }'
```

## Job status and outputs

```bash
curl -sS "$NEMOFLIX_API_URL/api/jobs/<prompt_id>"
```

Status may be `pending`, `in_progress`, `completed`, `failed`, or unavailable depending on backend state.

When complete, the response includes normalized outputs:

```json
{
  "status": "completed",
  "outputs": [
    {"type": "video", "url": "http://.../view?..."}
  ]
}
```

Return the final video URL to the user.

## Consent rule

For image-to-video, identity, body, likeness, or future LoRA training flows, require confirmation that the user owns or has permission to use the uploaded image/person/likeness.

## Agent behavior

1. Interpret the user's creative request.
2. Choose `t2v` or `i2v`.
3. Choose practical defaults for width, height, frame count, FPS, and prompt wording.
4. Submit the job through `/api/video/generate`.
5. Track `/api/jobs/{prompt_id}`.
6. Return the generated output URL when complete, or the `prompt_id` if still running.

Do not use the ComfyUI browser UI. ComfyUI is only the headless execution engine behind Nemoflix.
