import ollama
import fitz
import io
from PIL import Image
import pytesseract

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import Optional
import uvicorn

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_CHARS = 8000  # Reduced for speed


# ----------------------------
# TEXT EXTRACTION
# ----------------------------
def extract_text(file_content: bytes, filename: str) -> str:
    ext = filename.split('.')[-1].lower()

    if ext == "pdf":
        doc = fitz.open(stream=file_content, filetype="pdf")
        text = "".join(page.get_text() for page in doc)
        return text

    elif ext in ["png", "jpg", "jpeg"]:
        image = Image.open(io.BytesIO(file_content))
        return pytesseract.image_to_string(image)

    elif ext == "txt":
        return file_content.decode("utf-8")

    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")


# ----------------------------
# SUMMARIZE API
# ----------------------------
@app.post("/api/summarize")
async def summarize(
    text_input: Optional[str] = Form(None),
    summary_type: Optional[str] = Form("short"),
    file: Optional[UploadFile] = File(None)
):
    content = ""

    if file:
        file_bytes = await file.read()
        content = extract_text(file_bytes, file.filename)
    elif text_input:
        content = text_input
    else:
        raise HTTPException(status_code=400, detail="No content provided")

    if not content.strip():
        raise HTTPException(status_code=400, detail="Empty content")

    content = content[:MAX_CHARS]

    style_prompt = {
        "short": "Summarize in 3-5 very short bullet points.",
        "medium": "Summarize in clear and concise bullet points.",
        "detailed": "Give structured summary with headings and detailed bullet points."
    }

    def generate():
        stream = ollama.chat(
            model="llama3.2",
            messages=[
                {
                    "role": "system",
                    "content": f"You are a fast professional summarizer. {style_prompt.get(summary_type)}"
                },
                {
                    "role": "user",
                    "content": content
                }
            ],
            stream=True,
        )

        for chunk in stream:
            if chunk.get("message"):
                yield chunk["message"]["content"]

    return StreamingResponse(generate(), media_type="text/plain")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)