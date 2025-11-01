from vanna.ollama import Ollama
from vanna.chromadb.chromadb_vector import ChromaDB_VectorStore

class MyVanna(ChromaDB_VectorStore, Ollama):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        Ollama.__init__(self, config=config)

vn = MyVanna(config={"model": "mistral"})
methods = [m for m in dir(vn) if any(k in m for k in ["train", "add", "sql", "ddl", "query", "ask", "generate"]) ]
print("\n".join(sorted(methods)))


