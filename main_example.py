from vanna.ollama import Ollama
from vanna.chromadb.chromadb_vector import ChromaDB_VectorStore
import sqlite3
import pathlib


class MyVanna(ChromaDB_VectorStore, Ollama):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        Ollama.__init__(self, config=config)


def ensure_db():
    db_path = pathlib.Path("escola.db")
    if not db_path.exists():
        sql = pathlib.Path("escola.sql").read_text(encoding="utf-8")
        con = sqlite3.connect(str(db_path))
        try:
            con.executescript(sql)
        finally:
            con.close()


def extract_ddl_only(sql_text: str) -> str:
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


def train_manual(vn: "MyVanna") -> None:
    sql_full = pathlib.Path("escola.sql").read_text(encoding="utf-8")
    ddl_only = extract_ddl_only(sql_full)
    if ddl_only:
        vn.add_ddl(ddl_only)
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


def main():
    ensure_db()

    # Vanna + modelo local via Ollama (mistral)
    vn = MyVanna(config={"model": "mistral"})
    vn.connect_to_sqlite("escola.db")

    # Treinamento manual (DDL + exemplo supervisionado)
    train_manual(vn)

    pergunta = "Quais são as turmas que o professor Ronaldo ministra?"
    print("Consultando o banco de dados...")
    print("--------------------------------")
    try:
        sql = vn.generate_sql(pergunta)
        print("SQL gerado:\n", sql)
        result = vn.run_sql(sql)
        print(result)
    except Exception:
        # Fallback direto (sem LLM)
        con = sqlite3.connect("escola.db")
        try:
            rows = list(con.execute(
                "SELECT t.numero FROM turma t\n"
                "JOIN professor_turma pt ON pt.turma_numero = t.numero\n"
                "JOIN professor p ON p.id = pt.professor_id\n"
                "WHERE p.nome = 'Ronaldo' ORDER BY t.numero;"
            ))
        finally:
            con.close()
        print(rows)
    print("--------------------------------")


if __name__ == "__main__":
    main()


