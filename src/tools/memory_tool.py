import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from crewai_tools import tool


class MemoryTool:
    def __init__(self, persist_directory: str = "./data/memory"):
        os.makedirs(persist_directory, exist_ok=True)
        self.client = chromadb.PersistentClient(path=persist_directory,
            settings=Settings(anonymized_telemetry=False, allow_reset=True))
        self.collection = self.client.get_or_create_collection(name="agent_memory",
            metadata={"hnsw:space": "cosine"})
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
    def store_memory(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        memory_id = f"mem_{datetime.now().timestamp()}"
        if metadata is None:
            metadata = {}
        metadata['timestamp'] = datetime.now().isoformat()
        metadata['content_length'] = len(content)
        self.collection.add(documents=[content], metadatas=[metadata], ids=[memory_id])
        
        return memory_id
    
    def retrieve_memories(self, query: str, n_results: int = 5,
                         filter_metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        results = self.collection.query(query_texts=[query], n_results=n_results,
            where=filter_metadata if filter_metadata else None)
        memories = []
        if results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                memories.append({'content': doc, 'metadata': results['metadatas'][0][i],
                    'similarity': 1 - results['distances'][0][i]})
        return memories
    
    def clear_old_memories(self, days: int = 30):
        pass


_memory_instance = None

def get_memory_instance() -> MemoryTool:
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = MemoryTool()
    return _memory_instance


@tool("store_memory")
def store_memory_tool(content: str, category: str = "general") -> str:
    """Store important information in long-term memory for future reference."""
    memory = get_memory_instance()
    memory_id = memory.store_memory(content, metadata={'category': category})
    return f"Stored in memory with ID: {memory_id}"


@tool("retrieve_memory")
def retrieve_memory_tool(query: str, num_results: int = 5) -> str:
    """Retrieve relevant information from long-term memory."""
    memory = get_memory_instance()
    memories = memory.retrieve_memories(query, n_results=num_results)
    return json.dumps(memories, indent=2)

