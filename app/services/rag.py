from google import genai
from app.services.embeddings import generate_query_embedding
from app.services.vectorstore import retrieve_relevant_chunks
from dotenv import load_dotenv
import os

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def generate_answer(prompt: str) -> str:
    try:
        response = client.models.generate_content(
            model=DEFAULT_MODEL,
            contents=prompt
        )
        return response.text or "No response was returned by the Gemini model."
    except Exception as exc:
        raise RuntimeError(f"Gemini generation failed: {exc}") from exc


def build_context(chunks: list[dict]) -> str:
    context = ""
    for i, chunk in enumerate(chunks):
        meta = chunk["metadata"]
        context += f"\n[Source {i+1}: {meta['doc_name']} | Type: {meta['doc_type']} | Chunk: {meta['chunk_index']}]\n"
        context += chunk["text"] + "\n"
    return context


def unique_sources(chunks: list[dict]) -> list[dict]:
    seen = set()
    unique = []
    for chunk in chunks:
        meta = chunk["metadata"]
        key = (meta.get("doc_name"), meta.get("doc_type"))
        if key not in seen:
            seen.add(key)
            unique.append({
                "doc_name": meta.get("doc_name"),
                "doc_type": meta.get("doc_type"),
                "chunk_index": meta.get("chunk_index")
            })
    return unique


def query_compliance(user_query: str) -> dict:
    query_embedding = generate_query_embedding(user_query)
    chunks = retrieve_relevant_chunks(query_embedding, n_results=5)
    context = build_context(chunks)

    prompt = f"""You are an expert legal compliance assistant. 
Your job is to answer compliance-related questions accurately based ONLY on the provided documents.
The documents include both regulations and company policies - reference BOTH when relevant.
Always cite the source document for every claim you make.
If the answer cannot be found in the documents, say "I could not find relevant information in the uploaded documents."

DOCUMENTS:
{context}

QUESTION:
{user_query}

ANSWER (with citations from both regulation and policy documents where applicable):"""

    try:
        answer = generate_answer(prompt)
    except Exception as exc:
        return {
            "answer": f"I could not generate an answer right now: {exc}",
            "sources": unique_sources(chunks)
        }

    return {"answer": answer, "sources": unique_sources(chunks)}


def compare_documents(regulation_query: str) -> dict:
    query_embedding = generate_query_embedding(regulation_query)

    regulation_chunks = retrieve_relevant_chunks(query_embedding, n_results=8, doc_type="regulation")
    policy_chunks = retrieve_relevant_chunks(query_embedding, n_results=8, doc_type="policy")

    if not regulation_chunks or not policy_chunks:
        fallback_chunks = retrieve_relevant_chunks(query_embedding, n_results=16)
        regulation_chunks = regulation_chunks or [c for c in fallback_chunks if c["metadata"].get("doc_type") == "regulation"]
        policy_chunks = policy_chunks or [c for c in fallback_chunks if c["metadata"].get("doc_type") == "policy"]

    chunks = regulation_chunks + policy_chunks

    prompt = f"""You are a compliance gap analysis expert.
Compare the company policy against the regulation and identify:
1. Areas of compliance
2. Gaps/violations & Risk level for each gap (LOW / MEDIUM / HIGH / CRITICAL)
3. Recommendations to Fix Each Gap

REGULATION:
{build_context(regulation_chunks)}

COMPANY POLICY:
{build_context(policy_chunks)}

GAP ANALYSIS REPORT:"""

    try:
        gap_analysis = generate_answer(prompt)
    except Exception as exc:
        return {
            "gap_analysis": f"Gap analysis could not be completed: {exc}",
            "sources": list(dict.fromkeys(c["metadata"]["doc_name"] for c in chunks))
        }

    return {
        "gap_analysis": gap_analysis,
        "sources": list(dict.fromkeys(c["metadata"]["doc_name"] for c in chunks))
    }


def analyze_document(doc_name: str, doc_type: str) -> dict:
    """
    Full document analysis pipeline - summary, risk score,
    key terms, risky clauses, recommendations.
    """
    
    from app.services.vectorstore import get_all_chunks_for_doc
    chunks = get_all_chunks_for_doc(doc_name)

    if not chunks:
        return {
            "doc_name": doc_name,
            "word_count": 0,
            "doc_category": "Unknown",
            "risk_level": "UNKNOWN",
            "risk_score": 0,
            "summary": "No content found for this document.",
            "key_terms": [],
            "risk_clauses": [],
            "recommendations": []
        }

    full_text = " ".join([c["text"] for c in chunks])
    word_count = len(full_text.split())

    prompt = f"""You are an expert legal and compliance document analyst.
Analyze the following document and return a structured JSON response with exactly these fields:

{{
  "doc_category": "type of document e.g. Employment Policy, Legal Agreement, Regulation, Contract",
  "risk_level": "LOW or MEDIUM or HIGH or CRITICAL",
  "risk_score": a number from 0 to 100,
  "summary": "2-3 sentence plain language summary of the document",
  "key_terms": ["term1", "term2", "term3", "term4", "term5"],
  "risk_clauses": [
    {{"title": "clause name", "description": "why this is risky"}},
    {{"title": "clause name", "description": "why this is risky"}}
  ],
  "recommendations": [
    "recommendation 1",
    "recommendation 2",
    "recommendation 3"
  ]
}}

Rules:
- key_terms: extract 4-6 important legal/compliance terms found in the document
- risk_clauses: identify 2-4 risky or non-compliant sections
- recommendations: give 3-4 actionable steps
- Return ONLY the JSON, no extra text, no markdown code blocks

DOCUMENT ({doc_type}):
{full_text[:4000]}

JSON RESPONSE:"""

    try:
        raw = generate_answer(prompt)
        
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        import json
        parsed = json.loads(raw)

        return {
            "doc_name": doc_name,
            "word_count": word_count,
            "doc_category": parsed.get("doc_category", "Unknown"),
            "risk_level": parsed.get("risk_level", "UNKNOWN"),
            "risk_score": int(parsed.get("risk_score", 0)),
            "summary": parsed.get("summary", ""),
            "key_terms": parsed.get("key_terms", []),
            "risk_clauses": parsed.get("risk_clauses", []),
            "recommendations": parsed.get("recommendations", [])
        }

    except Exception as exc:
        return {
            "doc_name": doc_name,
            "word_count": word_count,
            "doc_category": doc_type.capitalize(),
            "risk_level": "UNKNOWN",
            "risk_score": 0,
            "summary": f"Analysis could not be completed: {exc}",
            "key_terms": [],
            "risk_clauses": [],
            "recommendations": []
        }
