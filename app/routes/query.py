from fastapi import APIRouter
from app.services.rag import query_compliance, compare_documents, analyze_document
from app.models.schemas import (
    QueryRequest, QueryResponse,
    GapAnalysisRequest, GapAnalysisResponse,
    DocumentAnalysisRequest, DocumentAnalysisResponse
)

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    result = query_compliance(request.question)
    return QueryResponse(**result)


@router.post("/gap-analysis", response_model=GapAnalysisResponse)
async def gap_analysis(request: GapAnalysisRequest):
    result = compare_documents(request.topic)
    return GapAnalysisResponse(**result)


@router.post("/analyze", response_model=DocumentAnalysisResponse)
async def analyze(request: DocumentAnalysisRequest):
    result = analyze_document(request.doc_name, request.doc_type)
    return DocumentAnalysisResponse(**result)