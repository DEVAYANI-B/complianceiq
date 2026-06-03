from pydantic import BaseModel

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    sources: list[dict]

class GapAnalysisRequest(BaseModel):
    topic: str

class GapAnalysisResponse(BaseModel):
    gap_analysis: str
    sources: list[str]

class UploadResponse(BaseModel):
    message: str
    doc_name: str
    doc_type: str
    chunks_stored: int

class DocumentAnalysisRequest(BaseModel):
    doc_name: str
    doc_type: str

class RiskClause(BaseModel):
    title: str
    description: str

class DocumentAnalysisResponse(BaseModel):
    doc_name: str
    word_count: int
    doc_category: str
    risk_level: str
    risk_score: int
    summary: str
    key_terms: list[str]
    risk_clauses: list[RiskClause]
    recommendations: list[str]