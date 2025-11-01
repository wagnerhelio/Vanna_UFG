from importlib.metadata import version  # opcional, só para validar ambiente
import sqlite3, pathlib

sql = pathlib.Path("escola.sql").read_text(encoding="utf-8")
con = sqlite3.connect("escola.db")
con.executescript(sql)
con.close()