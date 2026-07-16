from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


def search(query, text):

    paragraphs = text.split("\n")

    embeddings = model.encode(paragraphs)

    query_embedding = model.encode([query])

    similarity = cosine_similarity(
        query_embedding,
        embeddings
    )[0]

    top = np.argsort(similarity)[::-1][:5]

    return [paragraphs[i] for i in top]