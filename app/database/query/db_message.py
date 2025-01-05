# Created: dylannguyen
from typing import Optional
from sqlalchemy import select, text
from app.constant.config import OPENAPI_KEY
from app.database.models.message import Sessions, Messages
from sqlalchemy.orm import Session
from langchain_openai import OpenAIEmbeddings
from sqlalchemy.ext.asyncio import AsyncSession
from app.schema.conversation import ChatMessageHistory
from app.utils.azure_document_search import generate_embeddings

async def add_session(db: AsyncSession, session_id: str):
    new_session = Sessions(session_id=session_id)
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)
    return new_session

async def add_messages(
    db: AsyncSession, 
    session_id: str, 
    role: str, 
    content:str, 
    model:str= 'text-embedding-3-small'
) -> Messages:
    # escape single quote
    content = await escape_single_quote_helper(content)
    
    # generate the embedding
    embedding = await generate_embeddings(text = content, dimensions=1536)
    
    session = await db.execute(
        select(Sessions).where(Sessions.session_id == session_id)
    ) 
    session = session.scalars().one_or_none()
    if not session:
        await add_session(db=db, session_id=session_id)
        
    new_message = Messages(session_id=session_id, role=role, content=content, embedding=embedding)
    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)
    
    return new_message  

async def load_session_history(db: AsyncSession, session_id:int, limit: Optional[int] = 20) -> ChatMessageHistory:
    result = await db.execute(
        select(Messages)
        .where(Messages.session_id == session_id)
        .order_by(Messages.created_at.desc())
        .limit(limit)
    )
    
    messages = result.scalars().all()
    return messages
    
async def retrieve_similar_messages(
    db: AsyncSession, 
    query: str, 
    session_id: str,
    model: str='text-embedding-3-small',  
    top_k = 5
):
    # generate the embedding
    escaped_query = await escape_single_quote_helper(query)
    embeddings = OpenAIEmbeddings(model=model, api_key=OPENAPI_KEY)
    embedding = embeddings.embed_query(escaped_query)
    embedding_string = f"[{','.join(str(x) for x in embedding)}]"
    
    query_string= text(f"""
            SELECT role, content, created_at, 1-(embedding <=> :query_embedding) as cosine_similarity
            FROM public.\"SYS_MESSAGES\"
            WHERE session_id = :session_id
            ORDER BY cosine_similarity DESC
            LIMIT :top_k
        """)
    result = await db.execute(query_string, {
            "session_id": session_id,
            "query_embedding": embedding_string,
            "top_k": top_k
        })
    rows = result.fetchall()
    
    similar_messages = [
        {
            "role": row[0], 
            "content": row[1],
            "created_at": row[2]
        } for row in rows ]
    return similar_messages
    
async def escape_single_quote_helper(text):
    return text.replace("'","''")