from fastapi import FastAPI, Request
from pydantic import BaseModel
import os
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv

# Embeddings & Vector Store
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Gemini & Modern LangChain Chains
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# ----------------------------------------------------
# FastAPI Setup
# ----------------------------------------------------
app = FastAPI(
    title="AI Research Paper Assistant",
    version="1.0"
)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="template")

# ----------------------------------------------------
# Environment Variables
# ----------------------------------------------------
load_dotenv()

# ----------------------------------------------------
# Load Saved Embedding Model
# ----------------------------------------------------
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# ----------------------------------------------------
# Load Existing Chroma Database
# ----------------------------------------------------
vectordb = Chroma(
    persist_directory="research_db",
    embedding_function=embedding_model
)

retriever = vectordb.as_retriever(
    search_kwargs={"k": 3}
)

# ----------------------------------------------------
# Load Gemini & Modern RAG Chain
# ----------------------------------------------------
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0
)

# Define how the LLM should answer using the retrieved context
system_prompt = (
    "You are an assistant for question-answering tasks. "
    "Use the following pieces of retrieved context to answer "
    "the question. If you don't know the answer, say that you "
    "don't know.\n\n"
    "Context:\n{context}"
)

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}"),
])

# Create the document combining chain (Replaces "stuff" chain type)
question_answer_chain = create_stuff_documents_chain(llm, prompt)

# Create the final retrieval chain (Replaces RetrievalQA)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

# ----------------------------------------------------
# Request Models
# ----------------------------------------------------
class QueryRequest(BaseModel):
    query: str
    k: int = 3


class AskRequest(BaseModel):
    question: str


# ----------------------------------------------------
# Home Endpoint
# ----------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

# ----------------------------------------------------
# Search Endpoint
# ----------------------------------------------------
@app.post("/project")
def search_documents(request: QueryRequest):
    docs = vectordb.similarity_search(
        request.query,
        k=request.k
    )
    return {
        "query": request.query,
        "results": [
            {
                "content": doc.page_content,
                "metadata": doc.metadata
            }
            for doc in docs
        ]
    }

# ----------------------------------------------------
# Ask Endpoint (RAG)
# ----------------------------------------------------
@app.post("/ask")
def ask_question(request: AskRequest):
    # Modern chains use "input" instead of "query"
    response = rag_chain.invoke(
        {"input": request.question}
    )

    # Modern chains return "answer" instead of "result"
    return {
        "question": request.question,
        "answer": response["answer"]
    }
