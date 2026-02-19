from fastapi import APIRouter, HTTPException, BackgroundTasks
from mugeshbabu_agents.domain.chat.service import chat_service
from mugeshbabu_agents.domain.chat.models import ChatRequest, ChatResponse

router = APIRouter()

@router.post("/message", response_model=ChatResponse)
async def chat_message(request: ChatRequest):
    """
    Send a message to the chat agent regarding a document.
    """
    try:
        response = await chat_service.chat(
            project_id=request.project_id,
            document_url=request.document_url,
            question=request.question,
            conversation_id=request.conversation_id
        )
        return response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
