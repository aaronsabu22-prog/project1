from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
import shutil
import os

from utils.pdf_reader import extract_text
from utils.summarizer import generate_summary
from utils.qa import answer_question
from utils.semantic_search import search

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://aaronsabu22-prog.github.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

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

    filepath = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    paper_text = extract_text(filepath)

    return {
        "message": "Research paper uploaded successfully."
    }


@app.get("/summary")
async def summary():

    global paper_text

    if paper_text == "":
        return {
            "summary": "Please upload a research paper first."
        }

    summary = generate_summary(paper_text)

    return {
        "summary": summary
    }


@app.post("/ask")
async def ask(question: str = Form(...)):

    global paper_text

    if paper_text == "":
        return {
            "answer": "Please upload a research paper first."
        }

    answer = answer_question(
        question,
        paper_text
    )

    return {
        "answer": answer
    }


@app.post("/search")
async def semantic_search(query: str = Form(...)):

    global paper_text

    if paper_text == "":
        return {
            "results": []
        }

    results = search(
        query,
        paper_text
    )

    return {
        "results": results
    }


@app.get("/clear")
async def clear():

    global paper_text

    paper_text = ""

    return {
        "message": "Research paper cleared."
    }