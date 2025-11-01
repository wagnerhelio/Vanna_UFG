from flask import Flask, request, redirect, url_for, render_template_string
from vanna.ollama import Ollama
from vanna.chromadb.chromadb_vector import ChromaDB_VectorStore
import sqlite3
import pathlib
import pandas as pd


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


ensure_db()
vn = MyVanna(config={"model": "mistral"})
vn.connect_to_sqlite("escola.db")
train_manual(vn)


app = Flask(__name__)

PAGE = """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>Vanna Web - Escola</title>
    <style>
      body { font-family: Arial, sans-serif; margin: 24px; }
      .container { max-width: 960px; margin: auto; }
      textarea { width: 100%; height: 100px; font-size: 14px; }
      pre { background: #f6f8fa; padding: 12px; overflow: auto; }
      .card { border: 1px solid #ddd; border-radius: 6px; padding: 16px; margin-top: 16px; }
      .btn { background: #0d6efd; color: #fff; border: none; padding: 10px 16px; border-radius: 4px; cursor: pointer; }
      .btn:disabled { opacity: .7; cursor: not-allowed; }
      table { border-collapse: collapse; width: 100%; }
      th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
      th { background: #f0f0f0; }
      .muted { color: #666; font-size: 12px; }
    </style>
  </head>
  <body>
    <div class="container">
      <h1>Vanna Web - Escola</h1>
      <form method="post" action="{{ url_for('ask') }}">
        <label for="q">Pergunta</label>
        <textarea id="q" name="q" placeholder="Digite sua pergunta...">{{ q or '' }}</textarea>
        <div style="margin-top: 8px;">
          <button class="btn" type="submit">Perguntar</button>
        </div>
      </form>

      {% if sql %}
      <div class="card">
        <h3>SQL gerada</h3>
        <pre>{{ sql }}</pre>
      </div>
      {% endif %}

      {% if error %}
      <div class="card">
        <h3>Erro</h3>
        <pre>{{ error }}</pre>
      </div>
      {% endif %}

      {% if table_html %}
      <div class="card">
        <h3>Resultado</h3>
        {{ table_html | safe }}
      </div>
      {% elif rows %}
      <div class="card">
        <h3>Resultado (fallback)</h3>
        <pre>{{ rows }}</pre>
        <div class="muted">Obs: fallback executado sem LLM.</div>
      </div>
      {% endif %}

      <div class="muted" style="margin-top: 16px;">
        Dica: exemplo — "Quais são as turmas que o professor Ronaldo ministra?"
      </div>
    </div>
  </body>
  </html>
"""


@app.get("/")
def index():
    return render_template_string(PAGE)


@app.post("/ask")
def ask():
    q = (request.form.get("q") or "").strip()
    if not q:
        return redirect(url_for("index"))

    sql_text = None
    table_html = None
    rows = None
    error = None
    try:
        sql_text = vn.generate_sql(q)
        df = vn.run_sql(sql_text)
        if isinstance(df, pd.DataFrame):
            table_html = df.to_html(index=False)
        else:
            # Caso a integração retorne list/tuples
            rows = list(df)
    except Exception as exc:
        # fallback: tenta uma execução conhecida para a pergunta do Ronaldo
        error = str(exc)
        if "Ronaldo" in q:
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

    return render_template_string(PAGE, q=q, sql=sql_text, table_html=table_html, rows=rows, error=error)


if __name__ == "__main__":
    # Porta 8084 para manter padrão com exemplos anteriores
    app.run(host="0.0.0.0", port=8084)


