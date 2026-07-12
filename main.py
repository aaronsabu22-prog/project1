import os
import shutil

from dotenv import load_dotenv

from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from pydantic import BaseModel

# ------------------------------
# LlamaIndex
# ------------------------------
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    Settings,
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.storage.storage_context import StorageContext

import chromadb

# ------------------------------
# Load Environment Variables
# ------------------------------
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# ------------------------------
# FastAPI
# ------------------------------
app = FastAPI(
    title="AI Research Paper Assistant",
    version="2.0",
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="template")

# ------------------------------
# LlamaIndex Settings
# ------------------------------
Settings.embed_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
Settings.llm = GoogleGenAI(
    model="gemini-2.5-flash",
    api_key=GOOGLE_API_KEY,
)

# ------------------------------
# Chroma Vector DB
# ------------------------------
client = chromadb.PersistentClient(path="research_db")
collection = client.get_or_create_collection("research_papers")
vector_store = ChromaVectorStore(chroma_collection=collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# ------------------------------
# Globals
# ------------------------------
index = None
query_engine = None
documents = None


# ------------------------------
# Request Schemas
# ------------------------------
class AskRequest(BaseModel):
    question: str


class SearchRequest(BaseModel):
    query: str


# ------------------------------
# Routes
# ------------------------------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request},
    )


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    global index, query_engine, documents

    os.makedirs("uploads", exist_ok=True)
    filepath = os.path.join("uploads", file.filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    documents = SimpleDirectoryReader("uploads").load_data()
    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
    )
    query_engine = index.as_query_engine(similarity_top_k=5)

    return {
        "status": "success",
        "message": "Research paper uploaded successfully.",
    }


@app.post("/summary")
async def generate_summary():
    global query_engine

    if query_engine is None:
        return {
            "status": "error",
            "message": "Please upload a research paper first.",
        }

    prompt = """
    Analyze the uploaded research paper and generate a structured summary.

    Include:

    1. Paper Title
    2. Research Objective
    3. Problem Statement
    4. Methodology
    5. Dataset Used
    6. Algorithms / Models
    7. Results
    8. Advantages
    9. Limitations
    10. Future Scope

    Make the summary easy to understand.
    """

    response = query_engine.query(prompt)
    return {"status": "success", "summary": str(response)}


@app.post("/ask")
async def ask_question(request: AskRequest):
    global query_engine

    if query_engine is None:
        return {
            "status": "error",
            "message": "Please upload a paper first.",
        }

    prompt = f"""
    You are an AI Research Paper Assistant.

    Answer ONLY using the uploaded research paper.

    If the answer is not found, reply:

    "I could not find this information in the uploaded paper."

    Question:

    {request.question}
    """

    response = query_engine.query(prompt)
    return {
        "status": "success",
        "question": request.question,
        "answer": str(response),
    }


@app.post("/search")
async def search_paper(request: SearchRequest):
    global index

    if index is None:
        return {
            "status": "error",
            "message": "Please upload a paper first.",
        }

    retriever = index.as_retriever(similarity_top_k=5)
    nodes = retriever.retrieve(request.query)

    results = [{"score": node.score, "content": node.text} for node in nodes]

    return {"status": "success", "results": results}


@app.delete("/clear")
async def clear_database():
    global index, query_engine, documents

    index = None
    query_engine = None
    documents = None

    if os.path.exists("uploads"):
        shutil.rmtree("uploads")
    os.makedirs("uploads")

    return {
        "status": "success",
        "message": "All uploaded papers removed.",
    }


@app.get("/health")
async def health():
    return {
        "status": "running",
        "application": "AI Research Paper Assistant",
    }