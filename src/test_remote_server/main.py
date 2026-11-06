from fastmcp import FastMCP
from contextlib import closing
from datetime import datetime
import os
import sqlite3
import tempfile

# Writable location; override with an env var if you attach persistent storage
DB_PATH = os.environ.get(
    "EXPENSE_DB_PATH",
    os.path.join(tempfile.gettempdir(), "expenses.db"),
)

mcp = FastMCP("MyExpenseTracker")


def get_conn():
    return closing(sqlite3.connect(DB_PATH))


def init_db():
    with get_conn() as c:
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT DEFAULT '',
                note TEXT DEFAULT ''
            )
            """
        )
        c.commit()


def validate_date(d: str) -> str:
    datetime.strptime(d, "%Y-%m-%d")  # raises ValueError if invalid
    return d


init_db()


@mcp.tool
def add_expenses(date: str, amount: float, category: str,
                 subcategory: str = "", note: str = "") -> dict:
    """Add a new expense entry. Date must be YYYY-MM-DD."""
    validate_date(date)
    with get_conn() as c:
        cur = c.execute(
            "INSERT INTO expenses(date, amount, category, subcategory, note) "
            "VALUES (?,?,?,?,?)",
            (date, amount, category, subcategory, note),
        )
        c.commit()
        return {"status": "ok", "id": cur.lastrowid}


@mcp.tool
def list_expenses(start_date: str, end_date: str) -> list[dict]:
    """List all expenses in a date range (YYYY-MM-DD)."""
    validate_date(start_date); validate_date(end_date)
    with get_conn() as c:
        cur = c.execute(
            """SELECT id, date, amount, category, subcategory, note
               FROM expenses
               WHERE date BETWEEN ? AND ?
               ORDER BY id ASC""",
            (start_date, end_date),
        )
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]


@mcp.tool
def summarize(start_date: str, end_date: str, category: str | None = None) -> list[dict]:
    """Total expenses per category in a date range (YYYY-MM-DD)."""
    validate_date(start_date); validate_date(end_date)
    query = """
        SELECT category, SUM(amount) AS total_amount
        FROM expenses
        WHERE date BETWEEN ? AND ?
    """
    params = [start_date, end_date]
    if category:
        query += " AND category = ?"
        params.append(category)
    query += " GROUP BY category ORDER BY category ASC"

    with get_conn() as c:
        cur = c.execute(query, params)
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)