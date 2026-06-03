from fastapi import FastAPI
from app.routes.upload import router as upload_router
from app.routes.query import router as query_router

app = FastAPI(
    title="ComplianceIQ",
    description="Intelligent Legal Compliance Assistant powered by Google Gemini + RAG",
    version="1.0.0"
)

app.include_router(upload_router, prefix="/api", tags=["Upload"])
app.include_router(query_router, prefix="/api", tags=["Query"])


@app.get("/")
def root():
    return {"message": "ComplianceIQ API is running"}
