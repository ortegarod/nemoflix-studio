import uvicorn

uvicorn.run("nemoflix_amd.api:app", host="0.0.0.0", port=8190, reload=False)
