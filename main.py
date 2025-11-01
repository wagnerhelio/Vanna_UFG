# Importa classes do Vanna para LLM local (Ollama) e vetor de embeddings (ChromaDB)
from vanna.ollama import Ollama  
from vanna.chromadb.chromadb_vector import ChromaDB_VectorStore 
from vanna.flask import VannaFlaskApp
import pathlib
import sqlite3

# Definimos uma classe combinando o VectorStore local e o LLM local
class MyVanna(ChromaDB_VectorStore, Ollama):  
    def __init__(self, config=None):  
        # Inicializa o armazenamento vetorial (ChromaDB) 
        ChromaDB_VectorStore.__init__(self, config=config)  
        # Inicializa o LLM local via Ollama
        Ollama.__init__(self, config=config)


def extract_ddl_only(sql_text: str) -> str:
    """Extrai apenas blocos CREATE TABLE do script SQL, ignorando inserts/pragma."""
    lines = sql_text.splitlines()
    ddl_blocks = []
    capturing = False
    current = []
    for raw in lines:
        line = raw.strip()
        if not capturing and line.upper().startswith("CREATE TABLE"):
            capturing = True
            current = [raw]
            continue
        if capturing:
            current.append(raw)
            if line.endswith(");"):
                ddl_blocks.append("\n".join(current))
                capturing = False
                current = []
    return "\n\n".join(ddl_blocks)


def ensure_db():
    # Cria o banco a partir do arquivo se ainda não existir
    db_path = pathlib.Path("escola.db")
    if not db_path.exists():
        sql = pathlib.Path("escola.sql").read_text(encoding="utf-8")
        con = sqlite3.connect(str(db_path))
        try:
            con.executescript(sql)
        finally:
            con.close()


def main():
    ensure_db()

    # Instancia o "agente" Vanna configurado para usar o modelo local Mistral 
    vn = MyVanna(config={"model": "mistral"})

    # Conecta o Vanna ao banco de dados SQLite local:
    vn.connect_to_sqlite("escola.db")

    # Treina com o DDL para dar contexto de esquema
    sql_full = pathlib.Path("escola.sql").read_text(encoding="utf-8")
    ddl_only = extract_ddl_only(sql_full)
    if ddl_only:
        vn.add_ddl(ddl_only)

    # Opcional: adiciona um exemplo supervisionado para melhorar a primeira resposta
    example_q = "Quais são as turmas que o professor Ronaldo ministra?"
    example_sql = (
        "SELECT t.numero\n"
        "FROM turma t\n"
        "JOIN professor_turma pt ON pt.turma_numero = t.numero\n"
        "JOIN professor p ON p.id = pt.professor_id\n"
        "WHERE p.nome = 'Ronaldo'\n"
        "ORDER BY t.numero;"
    )
    vn.add_question_sql(question=example_q, sql=example_sql)
    vn.train()

    pergunta = example_q
    print("Consultando o banco de dados...")
    print("--------------------------------")
    try:
        # Fluxo via LLM: gerar SQL e executar
        sql = vn.generate_sql(pergunta)
        print("SQL gerado:\n", sql)
        result = vn.run_sql(sql)
        print(result)
    except Exception as e:
        # Fallback: executa um SQL conhecido caso o LLM/Ollama não esteja disponível
        print("Aviso: não foi possível usar o LLM (Ollama). Usando SQL de fallback.")
        con = sqlite3.connect("escola.db")
        try:
            rows = list(con.execute(example_sql))
        finally:
            con.close()
        print(rows)
    print("--------------------------------")


if __name__ == "__main__":
    main()

