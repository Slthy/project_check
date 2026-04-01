import pymysql
import pymysql.cursors
import os
import re
import sys


DB_CONFIG = {
    'host':     'regs26-borsato.cng0skw0wk8a.us-east-1.rds.amazonaws.com',
    'port':     3306,
    'database': 'university',
    'user':     'birdsarenotreal',
    'password': 'birdsarenotreal123',
    'cursorclass': pymysql.cursors.DictCursor,
    'charset':  'utf8mb4',
}

def split_statements(sql: str) -> list[str]:

    sql = re.sub(r'--[^\n]*', '', sql)
    sql = re.sub(r'#[^\n]*',  '', sql)
    sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)

    statements = []
    for raw in sql.split(';'):
        stmt = raw.strip()
        if stmt:
            statements.append(stmt)
    return statements
def run() -> None:
    sql_path = os.path.join(os.path.dirname(__file__), 'create_db.sql')
    if not os.path.exists(sql_path):
        print(f"[ERROR] SQL file not found: {sql_path}")
        sys.exit(1)

    print(f"[INFO]  Reading {sql_path} ...")
    with open(sql_path, 'r', encoding='utf-8') as f:
        raw_sql = f.read()

    statements = split_statements(raw_sql)
    print(f"[INFO]  {len(statements)} statement(s) found.")

    conn = None
    try:
        print(f"[INFO]  Connecting to {DB_CONFIG['host']} / {DB_CONFIG['database']} ...")
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        ok = 0
        errors = 0
        for i, stmt in enumerate(statements, start=1):
            try:
                cursor.execute(stmt)
                ok += 1
                preview = stmt.splitlines()[0][:80]
                print(f"  [{i:>4}] OK  — {preview}")

            except pymysql.Error as e:
                errors += 1
                preview = stmt.splitlines()[0][:80]
                print(f"  [{i:>4}] ERR — {preview}")
                print(f"         {e}")

        conn.commit()

    except pymysql.OperationalError as e:
        print(f"[ERROR] Could not connect to database: {e}")
        sys.exit(1)
    finally:
        if conn:
            conn.close()

    print()
    print(f"[DONE]  {ok} succeeded, {errors} failed.")
    if errors:
        print("[WARN]  Some statements failed — check output above.")
        sys.exit(1)