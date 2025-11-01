# Passo a passo (Windows/PowerShell) – Demo Vanna + SQLite (escola)

1) Criar/ativar venv
```
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

2) Instalar dependências
```
pip install --upgrade pip
pip install vanna ollama
```

3) Preparar o modelo local no Ollama (fora do Python)
- Instale o Ollama se necessário: https://ollama.com/download
- No terminal do Ollama, baixe o modelo:
```
ollama pull mistral:latest
```

4) Criar o banco SQLite local a partir do script
```
python .\subir_db.py
python .\check_db.py   # opcional: confirma tabelas
```
Saída esperada (exemplo):
```
DB exists: True
Tables: ['especializacao', 'especializacao_turma', 'professor', 'professor_turma', 'turma']
```

5) Rodar a aplicação (treinamento + chat web)
- O `main.py` já está configurado para:
  - Conectar ao `escola.db`
  - Treinar o esquema (modo A: manual via DDL extraído de `escola.sql`)
  - Executar uma pergunta de teste
  - Subir a interface web do Vanna (Flask)

Execute:
```
python .\main.py
```
Acesse no navegador: http://localhost:8084

6) Perguntar no chat
- Ex.: "Quais são as turmas que o professor Ronaldo ministra?"
- O Vanna usará o esquema treinado para gerar SQL, executar no SQLite e retornar a resposta (tabela e, se fizer sentido, gráfico).

Notas
- PowerShell não suporta `sqlite3 escola.db < escola.sql`. Use Python (`subir_db.py`) para carregar o SQL.
- `PRAGMA foreign_keys = ON` é por conexão. Seu script já ativa na criação; em novas conexões, reative se precisar de validação.
- Treinamento alternativo (modo B): no `main.py` há `train_auto_from_sqlite_master(vn)` que usa `sqlite_master` e `vn.get_training_plan_generic(...)`. Você pode trocar o modo conforme desejar.
- Logs: o console mostra o SQL gerado e etapas do LLM/Chroma.

Links úteis
- DB Browser for SQLite: https://sqlitebrowser.org/dl/
- Base Chinook (exemplo): https://vanna.ai/Chinook.sqlite
- Chinook (Kaggle): https://www.kaggle.com/datasets/nancyalaswad90/chinook-sample-database
- Artigo (visão geral Vanna): https://www.toolify.ai/ai-news/vanna-ai-querying-databases-with-natural-language-processing-3395180
