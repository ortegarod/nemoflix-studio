# AMD Diffusion Models Course Notes

**Status:** note-taking scaffold created  
**Context:** AMD course directly relevant to ROCm, ComfyUI, and hackathon prep

---

## Why This Matters
This course is directly aligned with what we care about for the AMD hackathon:
- understanding diffusion model fundamentals
- making better speed vs quality tradeoffs
- using Diffusers on AMD hardware
- using ComfyUI for video workflows

---

## Course Agenda

1. **How diffusion models work**
2. **How to balance speed and quality**
3. **Run in Diffusers to generate images**
4. **Running ComfyUI to generate videos**
5. **Wrap up**

---

## Notes

### 1. How diffusion models work
- **Text encoder / CLIP:** takes the human prompt and converts it into machine-readable latent/embedding form, basically turning natural language into the representation the model can reason over.
- **VAE / latent diffusion:** the model does not usually work directly on full raw image pixels. Instead, it compresses the whole image into a smaller abstract representation, a compact map of the important visual information. Diffusion happens in that compressed latent space because it is much more efficient, then the VAE decodes the final latent back into a normal image. This is not really pixel-by-pixel tokenization, it is more like learned image compression into a feature space the model can work with efficiently.
- **U-Net / denoising:** this is the model that takes noisy latent information and gradually turns it into a real image. More technically, it looks at the current noisy latent, the prompt guidance, and the current timestep, then predicts what part of the current state is noise so that noise can be removed. This happens over and over across many timesteps. Usually this is the same denoising model being reused repeatedly, not a completely different model at each step.
- **Scheduler / pacing:** decides how the denoising process moves across timesteps. In plain terms, yes, it is part of what controls the speed vs quality tradeoff, but more specifically it controls the path the model takes while removing noise. Different schedulers can reach different quality, sharpness, stability, and speed characteristics even when using the same underlying model.

--