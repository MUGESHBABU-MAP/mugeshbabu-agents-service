from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from fastapi.responses import Response
from mugeshbabu_agents.domain.documents.pdf_service import pdf_service

router = APIRouter()

class PDFRequest(BaseModel):
    url: str

@router.post("/pdf")
async def generate_pdf(request: PDFRequest):
    """
    Generate a PDF from a URL. returns the PDF bytes.
    """
    try:
        pdf_bytes = await pdf_service.generate_pdf(request.url)
        return Response(content=pdf_bytes, media_type="application/pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
