from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from app.moderation import moderate_text

app = FastAPI(title="Moderation Service", version="1.0.0")

@app.get("/api/moderation/health")
async def health():
    return {"status": "ok"}

@app.post("/api/moderation/text")
async def moderate_input(text: str = Form(...)):
    result = moderate_text(text)
    return JSONResponse(content=result)

@app.post("/api/moderation/file")
async def moderate_file(file: UploadFile = File(...)):
    content = (await file.read()).decode("utf-8", errors="ignore")
    result = moderate_text(content)
    return JSONResponse(content=result)
