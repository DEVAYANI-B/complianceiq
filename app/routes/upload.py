from fastapi import APIRouter, UploadFile, File, Form
from app.services.ingestion import extract_text
from app.services.chunker import chunk_text
from app.services.embeddings import generate_embeddings
from app.services.vectorstore import store_chunks
from app.models.schemas import UploadResponse

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    doc_type: str = Form(...)  
):
    file_bytes = await file.read()
    
    
    text = extract_text(file_bytes, file.filename)
    
    
    chunks = chunk_text(text, file.filename, doc_type)
    
    
    texts = [c["text"] for c in chunks]
    embeddings = generate_embeddings(texts)
    
    
    store_chunks(chunks, embeddings)
    
    return UploadResponse(
        message="Document uploaded and indexed successfully",
        doc_name=file.filename,
        doc_type=doc_type,
        chunks_stored=len(chunks)
    )
