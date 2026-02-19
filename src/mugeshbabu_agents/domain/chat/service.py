import json
import logging
from typing import List, Optional
import httpx
from bs4 import BeautifulSoup
from rank_bm25 import BM25Okapi
import redis.asyncio as redis
from bson import ObjectId

from mugeshbabu_agents.core.config import settings
from mugeshbabu_agents.infrastructure.db import db_manager
from mugeshbabu_agents.domain.chat.models import Conversation, Message, ChatResponse

from mugeshbabu_agents.infrastructure.repository import BaseRepository

logger = logging.getLogger(__name__)

class ConversationRepository(BaseRepository[Conversation]):
    pass

class ChatService:
    def __init__(self):
        self.redis = redis.from_url(settings.redis.url, encoding="utf-8", decode_responses=True)
        # In a real app, initialize AWS Bedrock client here
        # self.bedrock = boto3.client("bedrock-runtime", region_name=settings.aws.region)

    async def _fetch_and_parse_url(self, url: str) -> str:
        """Fetch HTML from URL and extract text."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content, "html.parser")
            # Remove scripts and styles
            for script in soup(["script", "style"]):
                script.extract()
            text = soup.get_text(separator="\n")
            # Basic cleanup
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            return text

    def _chunk_text(self, text: str, chunk_size: int = 500) -> List[str]:
        """Split text into chunks (naive splitting for now)."""
        words = text.split()
        chunks = []
        current_chunk = []
        current_size = 0
        
        for word in words:
            current_chunk.append(word)
            current_size += len(word) + 1
            if current_size >= chunk_size:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_size = 0
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        return chunks

    async def _get_or_create_chunks(self, url: str) -> List[str]:
        """Check Redis for chunks, else fetch and process."""
        cache_key = f"doc_chunks:{url}"
        cached = await self.redis.get(cache_key)
        
        if cached:
            logger.info(f"Cache hit for {url}")
            return json.loads(cached)
        
        logger.info(f"Cache miss for {url}. Fetching and processing.")
        text = await self._fetch_and_parse_url(url)
        chunks = self._chunk_text(text)
        
        # Cache for 24h
        await self.redis.setex(cache_key, 86400, json.dumps(chunks))
        return chunks

    def _retrieve_context(self, query: str, chunks: List[str], top_k: int = 3) -> List[str]:
        """Retrieve relevant chunks using BM25."""
        if not chunks:
            return []
            
        tokenized_corpus = [chunk.split(" ") for chunk in chunks]
        bm25 = BM25Okapi(tokenized_corpus)
        tokenized_query = query.split(" ")
        top_chunks = bm25.get_top_n(tokenized_query, chunks, n=top_k)
        return top_chunks

    async def _generate_response(self, query: str, context: List[str], history: List[Message]) -> str:
        """
        Call AWS Bedrock to generate a response.
        """
        context_block = "\n\n".join(context)
        prompt = f"Context:\n{context_block}\n\nQuestion: {query}\n\nAnswer:"
        
        # Construct payload for Claude (Mocking the exact payload structure/call)
        # payload = {
        #     "anthropic_version": "bedrock-2023-05-31",
        #     "max_tokens": 1000,
        #     "messages": [
        #         {"role": "user", "content": prompt}
        #     ]
        # }
        
        # response = await self.bedrock.invoke_model(...)
        
        # MOCK RESPONSE
        return f"Based on the document, here is the answer to '{query}'. (Context from {len(context)} chunks)"

    async def chat(self, project_id: str, document_url: str, question: str, conversation_id: Optional[str] = None) -> ChatResponse:
        """
        Main RAG pipeline.
        """
        db = db_manager.get_master_db() # Using master DB for conversations for now, or use project_db
        # Re-reading prompt: "Save Q&A pair to mb_t_conversations in Mongo"
        # Prompt said `mb_t_conversations`. I'll use that collection name.
        
        # 1. Get Conversation or Create New
        repo = ConversationRepository(db, "mb_t_conversations", Conversation)
        
        if conversation_id:
            conversation = await repo.get(conversation_id)
            if not conversation:
                raise ValueError("Conversation not found")
        else:
            conversation = Conversation(
                project_id=project_id,
                document_url=document_url,
                messages=[]
            )
            conversation = await repo.create(conversation)

        # 2. Get Chunks (Cache/Process)
        chunks = await self._get_or_create_chunks(document_url)

        # 3. Retrieve Context
        relevant_chunks = self._retrieve_context(question, chunks)

        # 4. Generate Answer
        answer_text = await self._generate_response(question, relevant_chunks, conversation.messages)

        # 5. Update History
        user_msg = Message(role="user", content=question)
        assistant_msg = Message(role="assistant", content=answer_text)
        
        conversation.messages.append(user_msg)
        conversation.messages.append(assistant_msg)
        conversation.updated_at = datetime.utcnow()

        # 6. Save to DB
        # 6. Save to DB
        await repo.update(conversation.id, conversation.model_dump(by_alias=True, exclude={"id"}))

        return ChatResponse(
            answer=answer_text,
            source_chunks=relevant_chunks,
            conversation_id=str(conversation.id)
        )

chat_service = ChatService()
