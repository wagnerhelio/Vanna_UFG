import sqlite3
import os

print("DB exists:", os.path.exists("escola.db"))
con = sqlite3.connect("escola.db")
try:
    tables = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")]
    print("Tables:", tables)
finally:
    con.close()


