from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import shutil
import fitz
from transformers import pipeline
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

UPLOAD_FOLDER = "uploads"

summarizer = pipeline(
    "summarization",
    model="facebook/bart-large-cnn"
)

qa_pipeline = pipeline(
    "question-answering"
)

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

paper_text = ""


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    global paper_text

    path = f"{UPLOAD_FOLDER}/{file.filename}"

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    doc = fitz.open(path)

    text = ""

    for page in doc:
        text += page.get_text()

    paper_text = text

    return {"message": "Paper uploaded successfully."}


@app.get("/summary")
async def summary():
    global paper_text

    if paper_text == "":
        return {"summary": "Upload a paper first."}

    result = summarizer(
        paper_text[:3000],
        max_length=180,
        min_length=60,
        do_sample=False
    )

    return {"summary": result[0]["summary_text"]}


@app.post("/ask")
async def ask(question: str = Form(...)):
    global paper_text

    if paper_text == "":
        return {"answer": "Upload a paper first."}

    result = qa_pipeline(
        question=question,
        context=paper_text[:5000]
    )

    return {"answer": result["answer"]}


@app.post("/search")
async def search(query: str = Form(...)):
    global paper_text

    if paper_text == "":
        return {"results": []}

    paragraphs = paper_text.split("\n")

    para_embeddings = embedding_model.encode(paragraphs)

    query_embedding = embedding_model.encode([query])

    similarity = cosine_similarity(
        query_embedding,
        para_embeddings
    )[0]

    top = np.argsort(similarity)[::-1][:5]

    results = [paragraphs[i] for i in top]

    return {"results": results}


@app.get("/clear")
async def clear():
    global paper_text
    paper_text = ""
    return {"message": "Paper cleared."}