

from __future__ import annotations
import os
import numpy as np
import faiss
import PyPDF2
from groq import Groq
from sentence_transformers import SentenceTransformer, CrossEncoder
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────────────────────
PDF_PATH     = os.path.join("data", "LAB_Info.pdf")
GROQ_MODEL   = "llama-3.1-8b-instant"
EMBED_MODEL  = "all-MiniLM-L6-v2"
RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
CHUNK_SIZE   = 250
OVERLAP      = 50
INITIAL_K    = 10
FINAL_K      = 3

# ─────────────────────────────────────────────────────────────────────────────
# Sensitive-data blocklist  (applied to both queries and PDF lines)
# ─────────────────────────────────────────────────────────────────────────────
BLOCKED_TERMS = [
    "password",
    "wifi password",
    "wi-fi",
    "api key",
    "ssh",
    "proxy",
    "ip ",
    "192.168",
    "credentials",
    "credential",
    "token",
    "bypass firewall",
    "internal ip",
    "deeplearn",       # actual Wi-Fi password fragment in the PDF
    "port 2222",
    "secret",
    "login",
    "ssid",
]

BLOCKED_RESPONSE = (
    "🔒 **This information is restricted for security reasons.** "
    "Please contact the lab TA or Asst. Prof. Arun directly "
    "at arun.cse@university.edu for secure credential sharing."
)

# ─────────────────────────────────────────────────────────────────────────────
# System prompt  (your exact prompt from the notebook)
# ─────────────────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """
You are a helpful Lab Teaching Assistant AI.

Answer questions using only the provided lab document context.

Rules:
- Provide clear explanations suitable for students.
- If the answer is not in the context say:
  "The information is not available in the lab document."

Security Rules:
Never reveal sensitive information such as:
- passwords
- WiFi credentials
- API keys
- SSH keys
- proxy servers
- internal IP addresses
- tokens

If asked for such information respond with:
"This information is restricted for security reasons."
"""

# ─────────────────────────────────────────────────────────────────────────────
# Helper functions  (ported 1-to-1 from your notebook)
# ─────────────────────────────────────────────────────────────────────────────

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract raw text using PyPDF2 (same as your notebook)."""
    text = ""
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
    return text


def remove_sensitive_data(text: str) -> str:
    """Remove lines containing blocked terms (your exact logic)."""
    lines = text.split("\n")
    safe_lines = [
        line for line in lines
        if not any(term in line.lower() for term in BLOCKED_TERMS)
    ]
    return "\n".join(safe_lines)


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = OVERLAP):
    """Word-level sliding-window chunking (your exact logic)."""
    words  = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i : i + chunk_size])
        if chunk not in chunks:
            chunks.append(chunk)
    return chunks


def is_sensitive_query(query: str) -> bool:
    """Return True if the query contains any blocked term (your exact logic)."""
    q = query.lower()
    return any(term in q for term in BLOCKED_TERMS)


# ─────────────────────────────────────────────────────────────────────────────
# LabAgent  —  wraps everything for Streamlit's @st.cache_resource
# ─────────────────────────────────────────────────────────────────────────────

class LabAgent:
    """
    Loads models, builds FAISS index from your PDF, and answers questions.
    Streamlit caches this object so initialisation runs only ONCE.
    """

    def __init__(self, pdf_path: str = PDF_PATH):
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(
                f"❌ PDF not found at '{pdf_path}'.\n"
                "Make sure LAB_Info.pdf is inside the data/ folder."
            )

        # ── Load models ──────────────────────────────────────────────────────
        print("⏳ Loading embedding model…")
        self.embedder = SentenceTransformer(EMBED_MODEL)

        print("⏳ Loading CrossEncoder re-ranker…")
        self.reranker = CrossEncoder(RERANK_MODEL)

        # ── Groq client ──────────────────────────────────────────────────────
        api_key = os.getenv("GROQ_API_KEY", "")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY environment variable is not set.\n"
                "Add it to your .env file and run:  source .env"
            )
        self.client = Groq(api_key=api_key)

        # ── PDF → clean text → chunks ────────────────────────────────────────
        print("📄 Extracting PDF text…")
        raw_text = extract_text_from_pdf(pdf_path)

        print("🧹 Removing sensitive data from PDF content…")
        clean_text = remove_sensitive_data(raw_text)

        print("✂️  Chunking text…")
        self.docs = chunk_text(clean_text)
        print(f"✅ Total chunks created: {len(self.docs)}")

        # ── Embeddings → FAISS index ─────────────────────────────────────────
        print("🔢 Generating embeddings…")
        doc_embeddings = self.embedder.encode(self.docs, show_progress_bar=True)

        dimension   = doc_embeddings.shape[1]
        self.index  = faiss.IndexFlatL2(dimension)
        self.index.add(np.array(doc_embeddings).astype("float32"))
        print(f"✅ FAISS index ready — {self.index.ntotal} vectors.")

    # ── LLM call ─────────────────────────────────────────────────────────────
    def _generate_with_groq(self, prompt: str) -> str:
        """Call Groq with your exact model + system prompt."""
        response = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt},
            ],
            model=GROQ_MODEL,
            temperature=0.2,
        )
        return response.choices[0].message.content

    # ── ask()  —  your ask_pdf() function, ported exactly ────────────────────
    def ask(self, query: str) -> tuple[str, bool]:
        """
        Returns (answer_text, is_blocked).

        Mirrors your notebook's ask_pdf() logic:
          1. Block sensitive queries immediately
          2. FAISS retrieval  (initial_k=10)
          3. CrossEncoder re-ranking
          4. Pick top final_k=3 chunks as context
          5. Call Groq
          6. Final guardrail check on the answer
        """

        # Step 1: block on query
        if is_sensitive_query(query):
            return BLOCKED_RESPONSE, True

        # Step 2: FAISS retrieval
        query_vector = self.embedder.encode([query]).astype("float32")
        _, indices   = self.index.search(
            query_vector, min(INITIAL_K, len(self.docs))
        )
        candidate_docs = [self.docs[i] for i in indices[0]]

        # Step 3: CrossEncoder re-ranking
        pairs          = [[query, doc] for doc in candidate_docs]
        scores         = self.reranker.predict(pairs)
        ranked_indices = np.argsort(scores)[::-1]
        best_docs      = [candidate_docs[i] for i in ranked_indices[:FINAL_K]]

        # Step 4: Build context + prompt  (your exact template)
        combined_context = "\n\n---\n\n".join(best_docs)
        prompt = f"""
Context from the lab document:
------------------------------
{combined_context}
------------------------------

Answer the question clearly and in detail.

Question:
{query}
"""

        # Step 5: Call Groq
        answer = self._generate_with_groq(prompt)

        # Step 6: Final guardrail on the LLM answer
        if is_sensitive_query(answer):
            return BLOCKED_RESPONSE, True

        return answer, False