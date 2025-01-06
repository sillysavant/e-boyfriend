from app.assistance.memory_agent import MemoryAgent
from app.schema.conversation import ChatMessageHistory


async def save_memory_service(
    memory_agent: MemoryAgent,
    messages: ChatMessageHistory
):
    await memory_agent.save_information_to_index(messages=messages)