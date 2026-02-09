from dotenv import load_dotenv
load_dotenv()

from app.core.orchestrator import Orchestrator
from app.core.embeddings import embed_text
from app.core.vector_store import QdrantVectorStore

vector_store = QdrantVectorStore(embed_fn=embed_text)
orchestrator = Orchestrator(vector_store)

result = orchestrator.process("What are the security requirements?")
print(result['response'])