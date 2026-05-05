from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any, Literal
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from .comfy import ComfyClient
from .config import get_settings
from .workflows import WAN_NEGATIVE, build_wan22_i2v, build_wan22_t2v

app = FastAPI(
    title="Nemoflix AMD API",
    description="Agent-native API for driving ComfyUI video generation on AMD GPUs.",
    version="0.1.0",
)


class VideoGenerateRequest(BaseModel):
    mode: Literal["t2v", "i2v"] = "i2v"
    prompt: str = Field(min_length=1)
    image: str | None = Field(default=None, description="ComfyUI input filename for image-to-video")
    negative: str = WAN_NEGATIVE
    width: int = 1280
    height: int = 720
    length: int = Field(default=121, description="Frame count, not seconds")
    fps: int = 16
    seed: int | None = None
    filename_prefix: str = "nemoflix-amd/video"
    steps_high: int = 10
    steps_low: int = 10
    cfg_high: float = 3.5
    cfg_low: float = 3.5
    shift: float = 5.0
    sampler: str = "euler"
    scheduler: str = "simple"

    # I2V model overrides. Defaults target the official Comfy-Org Wan 2.2 I2V fp8 stack.
    high_model: str = "wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors"
    low_model: str = "wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors"
    vae: str = "wan_2.1_vae.safetensors"
    clip: str = "umt5_xxl_fp8_e4m3fn_scaled.safetensors"
    high_lora: str | None = None
    low_lora: str | None = None
    high_lora_strength: float = 1.0
    low_lora_strength: float = 1.0

    submit: bool = Field(default=True, description="false returns workflow JSON without queueing")


class VideoGenerateResponse(BaseModel):
    ok: bool
    mode: str
    prompt_id: str | None = None
    number: int | None = None
    node_errors: dict[str, Any] | None = None
    workflow: dict[str, Any] | None = None


class JobOutput(BaseModel):
    type: str
    filename: str
    subfolder: str = ""
    folder_type: str = "output"
    url: str


class JobStatusResponse(BaseModel):
    ok: bool
    prompt_id: str
    status: str
    progress: float | None = None
    queue_position: int | None = None
    outputs_count: int | None = None
    outputs: list[JobOutput] = []
    raw: dict[str, Any] | None = None


def comfy() -> ComfyClient:
    settings = get_settings()
    return ComfyClient(settings.comfy_url, settings.request_timeout_seconds)


@app.get("/api/health")
async def health() -> dict[str, Any]:
    client = comfy()
    try:
        stats = await client.get("/system_stats")
    except Exception as exc:  # noqa: BLE001 - return service health, not stack trace
        raise HTTPException(status_code=502, detail=f"ComfyUI unavailable: {exc}") from exc
    return {"ok": True, "comfy_url": client.base_url, "system_stats": stats}


@app.get("/api/comfy/{path:path}")
async def comfy_get(path: str) -> Any:
    """Read-only passthrough for Comfy discovery endpoints: models, queue, object_info, history, etc."""
    allowed_roots = ("system_stats", "object_info", "models", "queue", "history", "prompt", "features")
    if not path.startswith(allowed_roots):
        raise HTTPException(status_code=403, detail="Only read-only Comfy discovery/status paths are exposed here")
    return await comfy().get(f"/{path}")


@app.post("/api/images/upload")
async def upload_image(file: UploadFile = File(...)) -> dict[str, Any]:
    suffix = Path(file.filename or "upload.png").suffix or ".png"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp_path = Path(tmp.name)
        tmp.write(await file.read())
    try:
        result = await comfy().upload_image(tmp_path)
        return {"ok": True, "comfy": result, "image": result.get("name")}
    finally:
        tmp_path.unlink(missing_ok=True)


@app.post("/api/video/generate", response_model=VideoGenerateResponse)
async def generate_video(body: VideoGenerateRequest) -> VideoGenerateResponse:
    if body.mode == "i2v":
        if not body.image:
            raise HTTPException(status_code=400, detail="image is required for i2v mode. Upload first with /api/images/upload.")
        workflow = build_wan22_i2v(
            image=body.image,
            prompt=body.prompt,
            negative=body.negative,
            width=body.width,
            height=body.height,
            length=body.length,
            fps=body.fps,
            seed=body.seed,
            filename_prefix=body.filename_prefix,
            steps_high=body.steps_high,
            steps_low=body.steps_low,
            cfg_high=body.cfg_high,
            cfg_low=body.cfg_low,
            shift=body.shift,
            sampler=body.sampler,
            scheduler=body.scheduler,
            high_model=body.high_model,
            low_model=body.low_model,
            vae=body.vae,
            clip=body.clip,
            high_lora=body.high_lora,
            low_lora=body.low_lora,
            high_lora_strength=body.high_lora_strength,
            low_lora_strength=body.low_lora_strength,
        )
    else:
        workflow = build_wan22_t2v(
            prompt=body.prompt,
            negative=body.negative,
            width=body.width,
            height=body.height,
            length=body.length,
            fps=body.fps,
            seed=body.seed,
            filename_prefix=body.filename_prefix,
            steps_high=body.steps_high,
            steps_low=body.steps_low,
            cfg_high=body.cfg_high,
            cfg_low=body.cfg_low,
            shift=body.shift,
            sampler=body.sampler,
            scheduler=body.scheduler,
        )

    if not body.submit:
        return VideoGenerateResponse(ok=True, mode=body.mode, workflow=workflow)

    try:
        result = await comfy().queue_prompt(workflow, client_id=str(uuid4()))
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"ComfyUI prompt submission failed: {exc}") from exc

    return VideoGenerateResponse(
        ok="prompt_id" in result,
        mode=body.mode,
        prompt_id=result.get("prompt_id"),
        number=result.get("number"),
        node_errors=result.get("node_errors"),
    )


def _extract_outputs(history: dict[str, Any], client: ComfyClient) -> list[JobOutput]:
    outputs: list[JobOutput] = []
    records = history.values() if isinstance(history, dict) else []
    for record in records:
        node_outputs = record.get("outputs", {}) if isinstance(record, dict) else {}
        for node_output in node_outputs.values():
            if not isinstance(node_output, dict):
                continue
            for key, output_type in (("video", "video"), ("videos", "video"), ("gifs", "video"), ("images", "image")):
                for item in node_output.get(key, []) or []:
                    filename = item.get("filename")
                    if not filename:
                        continue
                    subfolder = item.get("subfolder", "")
                    folder_type = item.get("type", "output")
                    outputs.append(JobOutput(
                        type=output_type,
                        filename=filename,
                        subfolder=subfolder,
                        folder_type=folder_type,
                        url=client.view_url_sync(filename, subfolder=subfolder, folder_type=folder_type),
                    ))
    return outputs


def _extract_outputs_from_comfy_job(job: dict[str, Any], client: ComfyClient) -> list[JobOutput]:
    outputs = job.get("outputs", {}) if isinstance(job, dict) else {}
    if not isinstance(outputs, dict):
        return []
    return _extract_outputs({job.get("id", "job"): {"outputs": outputs}}, client)


async def _queue_position(client: ComfyClient, prompt_id: str) -> int | None:
    queue = await client.get("/queue")
    pending = queue.get("queue_pending", []) if isinstance(queue, dict) else []
    for index, item in enumerate(pending, start=1):
        if isinstance(item, list) and len(item) > 1 and item[1] == prompt_id:
            return index
    return None


@app.get("/api/jobs/{prompt_id}", response_model=JobStatusResponse)
async def job(prompt_id: str) -> JobStatusResponse:
    client = comfy()

    # ComfyUI's normalized jobs endpoint reports pending/in_progress/completed.
    # It is the right polling surface for UI status. Raw /history only exists after completion.
    try:
        comfy_job = await client.get(f"/api/jobs/{prompt_id}")
        outputs = _extract_outputs_from_comfy_job(comfy_job, client)
        status = comfy_job.get("status", "unknown")
        progress = 100.0 if status == "completed" else None
        position = await _queue_position(client, prompt_id) if status == "pending" else None
        return JobStatusResponse(
            ok=True,
            prompt_id=prompt_id,
            status=status,
            progress=progress,
            queue_position=position,
            outputs_count=comfy_job.get("outputs_count"),
            outputs=outputs,
            raw=comfy_job,
        )
    except Exception:
        # Older ComfyUI builds may not have /api/jobs/{id}; fall back to history.
        history = await client.get(f"/history/{prompt_id}")
        outputs = _extract_outputs(history, client)
        status = "completed" if outputs else ("queued_or_running" if history == {} else "unknown")
        progress = 100.0 if outputs else None
        return JobStatusResponse(ok=True, prompt_id=prompt_id, status=status, progress=progress, outputs=outputs, raw=history)
